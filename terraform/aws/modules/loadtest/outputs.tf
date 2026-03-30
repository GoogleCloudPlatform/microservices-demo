output "master_public_ip" {
  description = "Public IP of the Locust master instance"
  value       = aws_instance.master.public_ip
}

output "locust_ui_url" {
  description = "URL of the Locust web UI"
  value       = "http://${aws_instance.master.public_ip}:8089"
}

output "worker_private_ips" {
  description = "Private IPs of the Locust worker instances"
  value       = aws_instance.worker[*].private_ip
}
