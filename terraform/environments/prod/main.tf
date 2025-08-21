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
  enable_access_logs         = var.enable_alb_access_logs
  enable_deletion_protection = var.enable_alb_deletion_protection
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

  # Secrets for the application
  database_url_secret_arn = module.rds.database_url_secret_arn

  # Optional ECS configuration
  desired_count         = var.ecs_desired_count
  cpu                   = var.ecs_cpu
  memory                = var.ecs_memory
  min_capacity          = var.ecs_min_capacity
  max_capacity          = var.ecs_max_capacity
  log_retention_days    = var.ecs_log_retention_days
}
