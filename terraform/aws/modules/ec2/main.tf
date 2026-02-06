resource "aws_instance" "app" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  key_name               = var.key_name
  user_data              = file("${path.module}/script/userdata.sh")

  tags = {
    Name = "${var.project_name}-ec2"
  }
}
