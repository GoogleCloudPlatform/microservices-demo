resource "aws_instance" "db" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  key_name               = var.key_name

  user_data = <<-EOF
    #!/bin/bash
    set -euo pipefail
    yum update -y
    yum install -y mariadb105-server
    systemctl enable mariadb
    systemctl start mariadb
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${var.db_password}';"
    mysql -u root -p'${var.db_password}' -e "CREATE DATABASE IF NOT EXISTS onlineboutique;"
    mysql -u root -p'${var.db_password}' -e "CREATE USER IF NOT EXISTS '${var.db_username}'@'%' IDENTIFIED BY '${var.db_password}';"
    mysql -u root -p'${var.db_password}' -e "GRANT ALL PRIVILEGES ON onlineboutique.* TO '${var.db_username}'@'%'; FLUSH PRIVILEGES;"
  EOF

  tags = {
    Name = "${var.project_name}-db"
  }
}
