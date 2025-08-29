variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "vpc_endpoints_security_group_id" {
  description = "ID of the VPC endpoints security group"
  type        = string
}

variable "app_port" {
  description = "Port for the application (ECS tasks)"
  type        = number
  default     = 8000
}

variable "db_port" {
  description = "Port for the database (PostgreSQL)"
  type        = number
  default     = 5432
}

variable "http_port" {
  description = "HTTP port"
  type        = number
  default     = 80
}

variable "https_port" {
  description = "HTTPS port"
  type        = number
  default     = 443
}
