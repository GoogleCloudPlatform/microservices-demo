output "redis_secret_arn" {
  description = "ARN of the Secrets Manager secret storing the Redis password"
  value       = aws_secretsmanager_secret.redis_password.arn
}
