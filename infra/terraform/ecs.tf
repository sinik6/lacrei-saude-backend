# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.app_name}-${var.environment}"
  retention_in_days = 30

  tags = { Name = "${var.app_name}-${var.environment}-logs" }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = { Name = "${var.app_name}-${var.environment}-cluster" }
}

# Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.app_name}-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = var.app_name
    image = "${aws_ecr_repository.app.repository_url}:latest"

    portMappings = [{
      containerPort = var.container_port
      protocol      = "tcp"
    }]

    environment = [
      { name = "DJANGO_DEBUG", value = "False" },
      { name = "DJANGO_ALLOWED_HOSTS", value = "*" },
      { name = "DJANGO_LOG_LEVEL", value = var.environment == "production" ? "INFO" : "DEBUG" },
      { name = "POSTGRES_HOST", value = aws_db_instance.main.address },
      { name = "POSTGRES_PORT", value = "5432" },
      { name = "POSTGRES_DB", value = var.db_name },
      { name = "CORS_ALLOWED_ORIGINS", value = "*" },
    ]

    secrets = [
      { name = "DJANGO_SECRET_KEY", valueFrom = "${aws_secretsmanager_secret.django.arn}:secret_key::" },
      { name = "POSTGRES_USER", valueFrom = "${aws_secretsmanager_secret.db.arn}:username::" },
      { name = "POSTGRES_PASSWORD", valueFrom = "${aws_secretsmanager_secret.db.arn}:password::" },
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.app.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/api/v1/health/ || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = { Name = "${var.app_name}-${var.environment}-taskdef" }
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "${var.app_name}-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.app_name
    container_port   = var.container_port
  }

  deployment_controller {
    type = "ECS"
  }

  depends_on = [aws_lb_listener.http]

  tags = { Name = "${var.app_name}-${var.environment}-service" }
}

# Auto Scaling
resource "aws_appautoscaling_target" "app" {
  max_capacity       = var.environment == "production" ? 4 : 2
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.app_name}-${var.environment}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.app.resource_id
  scalable_dimension = aws_appautoscaling_target.app.scalable_dimension
  service_namespace  = aws_appautoscaling_target.app.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70
  }
}

# Outputs
output "ecr_repository_url" {
  value       = aws_ecr_repository.app.repository_url
  description = "URL do ECR para push de imagens"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.main.name
  description = "Nome do cluster ECS"
}

output "ecs_service_name" {
  value       = aws_ecs_service.app.name
  description = "Nome do serviço ECS"
}

output "rds_endpoint" {
  value       = aws_db_instance.main.address
  description = "Endpoint do RDS"
}
