# Secret pour le mot de passe Redis
resource "aws_secretsmanager_secret" "redis_password" {
  name = "${var.project_name}/redis-password"

  tags = {
    Name = "${var.project_name}-redis-password"
  }
}

resource "time_rotating" "redis" {
  rotation_days = 30
}

# Generer un mot de passe aleatoire
resource "random_password" "redis" {
  length  = 32
  special = false

  keepers = {
    rotation = time_rotating.redis.id
  }
}

# Stocker le mot de passe dans le secret
resource "aws_secretsmanager_secret_version" "redis_password" {
  secret_id = aws_secretsmanager_secret.redis_password.id
  secret_string = jsonencode({
    password = random_password.redis.result
  })
}
