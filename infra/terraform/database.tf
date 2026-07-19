# Secrets Manager - credenciais do banco
resource "random_password" "db_password" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "db" {
  name = "${var.app_name}/${var.environment}/database"
  tags = { Name = "${var.app_name}-${var.environment}-db-secret" }
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id = aws_secretsmanager_secret.db.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db_password.result
    dbname   = var.db_name
    host     = aws_db_instance.main.address
    port     = 5432
  })
}

# Secrets Manager - Django secret key
resource "random_password" "django_secret_key" {
  length  = 50
  special = true
}

resource "aws_secretsmanager_secret" "django" {
  name = "${var.app_name}/${var.environment}/django"
  tags = { Name = "${var.app_name}-${var.environment}-django-secret" }
}

resource "aws_secretsmanager_secret_version" "django" {
  secret_id = aws_secretsmanager_secret.django.id
  secret_string = jsonencode({
    secret_key = random_password.django_secret_key.result
  })
}

# RDS PostgreSQL
resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-${var.environment}-db-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = { Name = "${var.app_name}-${var.environment}-db-subnet" }
}

resource "aws_db_instance" "main" {
  identifier     = "${var.app_name}-${var.environment}"
  engine         = "postgres"
  engine_version = "16.3"
  instance_class = var.rds_instance_class

  allocated_storage     = var.rds_allocated_storage
  max_allocated_storage = 100
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_password.result

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible    = false
  skip_final_snapshot    = var.environment == "staging"
  backup_retention_period = var.environment == "production" ? 30 : 7
  deletion_protection    = var.environment == "production"

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = { Name = "${var.app_name}-${var.environment}-rds" }
}
