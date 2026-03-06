output "redis_secret_arn" {
  description = "ARN of the Secrets Manager secret storing the Redis password"
  value       = aws_secretsmanager_secret.redis_password.arn
}

output "db_secret_arn" {
  description = "ARN of the Secrets Manager secret storing the DB password"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "db_password" {
  description = "Generated database password"
  value       = random_password.db.result
  sensitive   = true
}

output "db_username" {
  description = "Database username"
  value       = "admin"
}
