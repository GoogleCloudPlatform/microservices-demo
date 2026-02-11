output "private_ip" {
  description = "Private IP of the database EC2 instance"
  value       = aws_instance.db.private_ip
}

output "instance_id" {
  description = "ID of the database EC2 instance"
  value       = aws_instance.db.id
}
