terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "hypochondriai-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "hypochondriai-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

# Local values for computed configurations
locals {
  # Base CORS origins for initial deployment
  base_cors_origins = var.ecs_cors_origins
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name         = var.project_name
  environment          = var.environment
  aws_region           = var.aws_region
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

# Security Groups Module
module "security" {
  source = "../../modules/security"

  project_name                    = var.project_name
  environment                     = var.environment
  vpc_id                          = module.vpc.vpc_id
  vpc_endpoints_security_group_id = module.vpc.vpc_endpoints_security_group_id
}

# ALB Module
module "alb" {
  source = "../../modules/alb"

  project_name           = var.project_name
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  public_subnet_ids     = module.vpc.public_subnet_ids
  alb_security_group_id = module.security.alb_security_group_id

  # Optional configuration
  enable_access_logs = var.enable_alb_access_logs
}

# RDS Module
module "rds" {
  source = "../../modules/rds"

  project_name          = var.project_name
  environment           = var.environment
  subnet_ids            = module.vpc.private_subnet_ids
  rds_security_group_id = module.security.rds_security_group_id

  # Optional overrides
  instance_class          = var.rds_instance_class
  backup_retention_period = var.rds_backup_retention_period
}

# ECR Module
module "ecr" {
  source = "../../modules/ecr"

  project_name = var.project_name
  environment  = var.environment

  # Optional ECR configuration
  repository_name      = var.ecr_repository_name
  image_tag_mutability = var.ecr_image_tag_mutability
  scan_on_push        = var.ecr_scan_on_push
  force_delete        = true
}

# Superuser secrets for initial application setup
resource "random_password" "superuser_password" {
  length  = 16
  special = true
  override_special = "!#$%^*-_=+[]{}:,.?"
  min_lower   = 1
  min_upper   = 1
  min_numeric = 1
  min_special = 1
}

resource "aws_secretsmanager_secret" "superuser_username" {
  name        = "${var.project_name}/${var.environment}/app/superuser-username"
  description = "Application superuser username"
  force_overwrite_replica_secret = true

  tags = {
    Name        = "${var.project_name}-superuser-username-secret"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "superuser_username" {
  secret_id     = aws_secretsmanager_secret.superuser_username.id
  secret_string = "admin"
}

resource "aws_secretsmanager_secret" "superuser_password" {
  name        = "${var.project_name}/${var.environment}/app/superuser-password"
  description = "Application superuser password"
  force_overwrite_replica_secret = true

  tags = {
    Name        = "${var.project_name}-superuser-password-secret"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "superuser_password" {
  secret_id     = aws_secretsmanager_secret.superuser_password.id
  secret_string = random_password.superuser_password.result
}

resource "aws_secretsmanager_secret" "superuser_email" {
  name        = "${var.project_name}/${var.environment}/app/superuser-email"
  description = "Application superuser email"
  force_overwrite_replica_secret = true

  tags = {
    Name        = "${var.project_name}-superuser-email-secret"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "superuser_email" {
  secret_id     = aws_secretsmanager_secret.superuser_email.id
  secret_string = "admin@hypochondriai.com"
}


# ECS Module
module "ecs" {
  source = "../../modules/ecs"

  project_name           = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  ecs_security_group_id = module.security.ecs_security_group_id
  target_group_arn      = module.alb.target_group_arn
  alb_arn               = module.alb.alb_arn

  # ECR repository from ECR module
  ecr_repository_url = module.ecr.repository_url

  # Secrets for the application
  database_url_secret_arn       = module.rds.database_url_secret_arn
  superuser_username_secret_arn = aws_secretsmanager_secret.superuser_username.arn
  superuser_password_secret_arn = aws_secretsmanager_secret.superuser_password.arn
  superuser_email_secret_arn    = aws_secretsmanager_secret.superuser_email.arn

  # Optional ECS configuration
  desired_count         = var.ecs_desired_count
  cpu                   = var.ecs_cpu
  memory                = var.ecs_memory
  min_capacity          = var.ecs_min_capacity
  max_capacity          = var.ecs_max_capacity
  log_retention_days    = var.ecs_log_retention_days
  cors_origins          = "${var.ecs_cors_origins},${module.s3_cloudfront.website_url}"

  depends_on = [module.s3_cloudfront]
}

# S3 + CloudFront Module for Frontend
module "s3_cloudfront" {
  source = "../../modules/s3-cloudfront"

  project_name = var.project_name
  environment  = var.environment

  # CloudFront configuration
  default_cache_ttl = var.cloudfront_default_cache_ttl
  max_cache_ttl     = var.cloudfront_max_cache_ttl
  static_cache_ttl  = var.cloudfront_static_cache_ttl
  price_class       = var.cloudfront_price_class

  # Custom domain configuration (optional)
  custom_domain         = var.cloudfront_custom_domain
  acm_certificate_arn   = var.cloudfront_acm_certificate_arn

  # WAF configuration (optional)
  web_acl_id = var.cloudfront_web_acl_id

  # Deployment user configuration
  create_deployment_user          = var.create_frontend_deployment_user
  create_access_keys             = var.create_frontend_access_keys
  store_keys_in_secrets_manager  = var.store_frontend_keys_in_secrets_manager

  tags = {
    Module = "s3-cloudfront"
  }
}
