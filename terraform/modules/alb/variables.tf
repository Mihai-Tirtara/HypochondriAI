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

variable "public_subnet_ids" {
  description = "IDs of the public subnets"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "ID of the ALB security group"
  type        = string
}

variable "domain_name" {
  description = "Custom domain name for the ALB (optional)"
  type        = string
  default     = null
}

variable "certificate_arn" {
  description = "ARN of existing SSL certificate (optional)"
  type        = string
  default     = null
}

variable "health_check_path" {
  description = "Health check path for target group"
  type        = string
  default     = "/docs"
}

variable "health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

variable "health_check_timeout" {
  description = "Health check timeout in seconds"
  type        = number
  default     = 5
}

variable "healthy_threshold" {
  description = "Number of consecutive successful health checks"
  type        = number
  default     = 2
}

variable "unhealthy_threshold" {
  description = "Number of consecutive failed health checks"
  type        = number
  default     = 2
}

variable "enable_access_logs" {
  description = "Enable ALB access logging"
  type        = bool
  default     = true
}

variable "app_port" {
  description = "Port for the application (ECS tasks)"
  type        = number
  default     = 8000
}
