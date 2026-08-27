output "repository_urls" {
  description = "Map of service name to its ECR repository URL"
  value       = { for k, v in aws_ecr_repository.this : k => v.repository_url }
}