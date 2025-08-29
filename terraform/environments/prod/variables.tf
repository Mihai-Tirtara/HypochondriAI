variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "hypochondriai"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["eu-central-1a", "eu-central-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

# ALB Configuration
variable "enable_alb_access_logs" {
  description = "Enable ALB access logging"
  type        = bool
  default     = false
}


# RDS Configuration
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_backup_retention_period" {
  description = "RDS backup retention period in days"
  type        = number
  default     = 7
}

# ECR Configuration
variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "backend"
}

variable "ecr_image_tag_mutability" {
  description = "ECR image tag mutability setting"
  type        = string
  default     = "IMMUTABLE"
}

variable "ecr_scan_on_push" {
  description = "Enable image scanning on push to ECR"
  type        = bool
  default     = true
}


# ECS Configuration
variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "ecs_cpu" {
  description = "CPU units for ECS task"
  type        = number
  default     = 512
}

variable "ecs_memory" {
  description = "Memory for ECS task in MB"
  type        = number
  default     = 1024
}

variable "ecs_min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 1
}

variable "ecs_max_capacity" {
  description = "Maximum number of ECS tasks"
  type        = number
  default     = 3
}

variable "ecs_log_retention_days" {
  description = "ECS log retention period in days"
  type        = number
  default     = 14
}

variable "ecs_cors_origins" {
  description = "Comma-separated list of allowed CORS origins for backend"
  type        = string
  default     = "http://localhost:3000"
}

# S3 + CloudFront Configuration
variable "cloudfront_default_cache_ttl" {
  description = "Default TTL for CloudFront cache in seconds"
  type        = number
  default     = 86400 # 24 hours
}

variable "cloudfront_max_cache_ttl" {
  description = "Maximum TTL for CloudFront cache in seconds"
  type        = number
  default     = 31536000 # 1 year
}

variable "cloudfront_static_cache_ttl" {
  description = "TTL for static assets (CSS, JS, images) in seconds"
  type        = number
  default     = 31536000 # 1 year
}

variable "cloudfront_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
}

variable "cloudfront_custom_domain" {
  description = "Custom domain name for CloudFront distribution (optional)"
  type        = string
  default     = null
}

variable "cloudfront_acm_certificate_arn" {
  description = "ACM certificate ARN for custom domain (required if custom_domain is set)"
  type        = string
  default     = null
}

variable "cloudfront_web_acl_id" {
  description = "AWS WAF web ACL ID to associate with CloudFront distribution (optional)"
  type        = string
  default     = null
}

# Frontend deployment configuration
variable "create_frontend_deployment_user" {
  description = "Create IAM user for frontend deployment"
  type        = bool
  default     = true
}

variable "create_frontend_access_keys" {
  description = "Create access keys for frontend deployment user"
  type        = bool
  default     = true
}

variable "store_frontend_keys_in_secrets_manager" {
  description = "Store frontend access keys in AWS Secrets Manager"
  type        = bool
  default     = true
}
