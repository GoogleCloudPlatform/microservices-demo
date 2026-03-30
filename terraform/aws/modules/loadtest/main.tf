# Security group for the Locust master
resource "aws_security_group" "master" {
  name        = "${var.project_name}-locust-master-sg"
  description = "Locust master: UI (8089), worker comm (5557-5558), SSH (22)"
  vpc_id      = var.vpc_id

  ingress {
    description = "Locust Web UI"
    from_port   = 8089
    to_port     = 8089
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Locust worker ZeroMQ"
    from_port   = 5557
    to_port     = 5558
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-locust-master-sg"
  }
}

# Security group for Locust workers (outbound only)
resource "aws_security_group" "worker" {
  name        = "${var.project_name}-locust-worker-sg"
  description = "Locust workers: outbound traffic to master and target"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-locust-worker-sg"
  }
}

# Locust master EC2 instance
resource "aws_instance" "master" {
  ami                         = var.ami_id
  instance_type               = var.instance_type_master
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.master.id]
  key_name                    = var.key_name
  associate_public_ip_address = true

  user_data = templatefile("${path.module}/scripts/master.sh", {
    locustfile_content = var.locustfile_content
    worker_count       = var.worker_count
    target_host        = var.target_host
  })

  tags = {
    Name = "${var.project_name}-locust-master"
  }
}

# Locust worker EC2 instances
resource "aws_instance" "worker" {
  count                       = var.worker_count
  ami                         = var.ami_id
  instance_type               = var.instance_type_worker
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.worker.id]
  key_name                    = var.key_name
  associate_public_ip_address = false

  user_data = templatefile("${path.module}/scripts/worker.sh.tpl", {
    locustfile_content = var.locustfile_content
    master_private_ip  = aws_instance.master.private_ip
    target_host        = var.target_host
  })

  depends_on = [aws_instance.master]

  tags = {
    Name = "${var.project_name}-locust-worker-${count.index + 1}"
  }
}
