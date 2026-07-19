# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.app_name}-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = { Name = "${var.app_name}-${var.environment}-alb" }
}

# Target Group
resource "aws_lb_target_group" "app" {
  name        = "${var.app_name}-${var.environment}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/api/v1/health/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200,503"
  }

  tags = { Name = "${var.app_name}-${var.environment}-tg" }
}

# Listener HTTP
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Output - URL do ALB
output "alb_dns_name" {
  value       = aws_lb.main.dns_name
  description = "DNS do Load Balancer"
}

output "api_url" {
  value       = "http://${aws_lb.main.dns_name}/api/v1/health/"
  description = "URL da API"
}
