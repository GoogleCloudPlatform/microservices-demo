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

# --- Secret pour le mot de passe de la base de donnees ---

resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.project_name}/db-password"

  tags = {
    Name = "${var.project_name}-db-password"
  }
}

resource "time_rotating" "db" {
  rotation_days = 30
}

resource "random_password" "db" {
  length  = 32
  special = false

  keepers = {
    rotation = time_rotating.db.id
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "admin"
    password = random_password.db.result
  })
}
