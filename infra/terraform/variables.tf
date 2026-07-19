variable "aws_region" {
  description = "Região AWS"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente: staging ou production"
  type        = string

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment deve ser 'staging' ou 'production'"
  }
}

variable "app_name" {
  description = "Nome da aplicação"
  type        = string
  default     = "lacrei-saude-api"
}

variable "container_port" {
  description = "Porta do container"
  type        = number
  default     = 8000
}

variable "ecs_task_cpu" {
  description = "CPU da task ECS"
  type        = number
  default     = 512
}

variable "ecs_task_memory" {
  description = "Memória da task ECS"
  type        = number
  default     = 1024
}

variable "ecs_desired_count" {
  description = "Número de instâncias"
  type        = number
  default     = 2
}

variable "rds_instance_class" {
  description = "Classe da instância RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  description = "Storage do RDS em GB"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Nome do banco"
  type        = string
  default     = "lacrei"
}

variable "db_username" {
  description = "Usuário do banco"
  type        = string
  default     = "lacrei_admin"
}

variable "domain_name" {
  description = "Domínio da API"
  type        = string
  default     = ""
}
