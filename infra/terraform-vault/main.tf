# Busca la VPC predeterminada del laboratorio.
data "aws_vpc" "default" {
  default = true
}

# Obtiene las subredes disponibles dentro de la VPC.
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Busca una imagen oficial y reciente de Ubuntu Server 22.04.
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group utilizado por el servidor de Vault.
resource "aws_security_group" "vault" {
  name        = "${var.project_name}-sg"
  description = "Acceso controlado al servidor de HashiCorp Vault"
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Name = "${var.project_name}-sg"
  }
}

# Acceso SSH para la configuración posterior con Ansible.
resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.vault.id
  description       = "SSH desde la IP autorizada"

  cidr_ipv4   = var.allowed_cidr
  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
}

# Acceso a la interfaz web y API de Vault.
resource "aws_vpc_security_group_ingress_rule" "vault_ui" {
  security_group_id = aws_security_group.vault.id
  description       = "Vault UI y API desde la IP autorizada"

  cidr_ipv4   = var.allowed_cidr
  from_port   = 8200
  to_port     = 8200
  ip_protocol = "tcp"
}

# Permite que la EC2 descargue actualizaciones y dependencias.
resource "aws_vpc_security_group_egress_rule" "outbound" {
  security_group_id = aws_security_group.vault.id
  description       = "Salida a Internet"

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
}

# Instancia EC2 independiente del clúster de Kubernetes.
resource "aws_instance" "vault" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.key_name

  subnet_id                   = sort(data.aws_subnets.default.ids)[0]
  vpc_security_group_ids      = [aws_security_group.vault.id]
  associate_public_ip_address = true

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    volume_size = 10
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "${var.project_name}-server"
  }
}
