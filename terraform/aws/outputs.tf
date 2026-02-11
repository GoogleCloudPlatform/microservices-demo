output "frontend_url" {
  description = "URL to access the Online Boutique frontend (via ALB)"
  value       = "http://${module.alb.alb_dns_name}"
}

output "ec2_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = module.ec2.public_ip
}

output "db_private_ip" {
  description = "Private IP of the database EC2 instance"
  value       = module.rds.private_ip
}
