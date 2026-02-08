# Secret pour le mot de passe Redis
resource "aws_secretsmanager_secret" "redis_password" {
  name = "${var.project_name}/redis-password"
}

# Generer un mot de passe aleatoire
resource "random_password" "redis" {
  length  = 32
  special = false
}

# Stocker le mot de passe dans le secret
resource "aws_secretsmanager_secret_version" "redis_password" {
  secret_id = aws_secretsmanager_secret.redis_password.id
  secret_string = jsonencode({
    password = random_password.redis.result
  })
}
