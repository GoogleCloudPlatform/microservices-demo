output "redis_secret_arn" {
  value = aws_secretsmanager_secret.redis_password.arn
}
