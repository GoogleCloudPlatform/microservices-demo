terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

#  Imagen: Ubuntu 24.04 LTS oficial de Canonical 
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

#  Red: la VPC por defecto (la misma que usa el clúster EKS) 
data "aws_vpc" "default" {
  default = true
}

data "aws_subnet" "vault" {
  vpc_id            = data.aws_vpc.default.id
  availability_zone = "us-east-1a"
  default_for_az    = true
}

#  Firewall: solo 8200 (Vault) y 22 (SSH desde TU IP) 
resource "aws_security_group" "vault" {
  name        = "vault-server-sg"
  description = "Vault: API/UI por 8200 (TLS) y SSH solo desde la IP del administrador"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Vault API y UI web (HTTPS). Abierto porque los runners de GitHub Actions no tienen IP fija; la proteccion es TLS + token + politicas ACL."
    from_port   = 8200
    to_port     = 8200
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH solo desde la IP del administrador (para Ansible)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  egress {
    description = "Salida a internet (paquetes apt, repositorio de HashiCorp)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

 
  tags = { Name = "vault-server-sg", Project = "online-boutique" }
}

#  El servidor 
resource "aws_instance" "vault" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name # "vockey" en AWS Academy
  subnet_id              = data.aws_subnet.vault.id
  vpc_security_group_ids = [aws_security_group.vault.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true # los datos de Vault quedan cifrados en reposo también a nivel disco
  }

  metadata_options {
    http_tokens = "required" # IMDSv2 obligatorio (buena práctica de seguridad)
  }
lifecycle {
    ignore_changes = [ami]
  }

  tags = { Name = "vault-server", Project = "online-boutique" }
}

#  IP fija: la dirección de Vault no cambia aunque la EC2 se reinicie 
resource "aws_eip" "vault" {
  instance = aws_instance.vault.id
  domain   = "vpc"
  tags     = { Name = "vault-server-eip", Project = "online-boutique" }
}

#  Genera automáticamente el inventario de Ansible 
resource "local_file" "ansible_inventory" {
  filename        = "${path.module}/../ansible/inventory.ini"
  file_permission = "0644"
  content         = <<-EOT
    # Generado automáticamente por terraform-vault/main.tf - no editar a mano.
    [vault]
    ${aws_eip.vault.public_ip} vault_public_ip=${aws_eip.vault.public_ip}

    [vault:vars]
    ansible_user=ubuntu
    ansible_ssh_private_key_file=~/.ssh/labsuser.pem
    ansible_python_interpreter=/usr/bin/python3
    # La IP elástica se reutiliza cuando se recrea el servidor (prueba de
    # idempotencia), lo que cambia la huella SSH; por eso no se fija en known_hosts.
    ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
  EOT
}
