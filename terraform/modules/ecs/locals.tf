locals {
  # Common tags to be applied to all resources
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Module      = "ecs"
  }

  # Container image tag (can be overridden via variable in the future)
  container_image_tag = "latest"

  # Full container image URI
  container_image_uri = "${var.ecr_repository_url}:${local.container_image_tag}"

  # ALB resource label for auto scaling (extracted from ALB ARN)
  # Format: app/load-balancer-name/1234567890123456
  alb_resource_label = var.alb_arn != null ? regex("app/([^/]+/[^/]+)", var.alb_arn)[0] : null

  # Target group resource label for auto scaling (extracted from target group ARN)
  # Format: targetgroup/target-group-name/1234567890123456
  target_group_resource_label = var.target_group_arn != null ? regex("(targetgroup/[^/]+/[^/]+)", var.target_group_arn)[0] : null

  # Environment-specific configuration
  environment_config = {
    prod = {
      enable_detailed_monitoring = true
      enable_container_insights  = true
      log_level                 = "INFO"
    }
    staging = {
      enable_detailed_monitoring = false
      enable_container_insights  = true
      log_level                 = "DEBUG"
    }
    dev = {
      enable_detailed_monitoring = false
      enable_container_insights  = false
      log_level                 = "DEBUG"
    }
  }

  # Current environment configuration
  current_env_config = local.environment_config[var.environment]

  # Health check configuration
  health_check_config = {
    command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}${var.health_check_path} || exit 1"]
    interval    = 30
    timeout     = 5
    retries     = 3
    startPeriod = 60
  }

  # Container resource configuration based on environment
  container_resources = {
    cpu    = var.cpu
    memory = var.memory
  }

  # Auto scaling configuration
  autoscaling_config = {
    min_capacity           = var.min_capacity
    max_capacity          = var.max_capacity
    cpu_target_value      = var.cpu_target_value
    memory_target_value   = var.memory_target_value
    scale_up_cooldown     = var.scale_up_cooldown
    scale_down_cooldown   = var.scale_down_cooldown
  }

  # CloudWatch log configuration
  log_config = {
    log_driver = "awslogs"
    options = {
      "awslogs-group"         = aws_cloudwatch_log_group.backend.name
      "awslogs-region"        = var.aws_region
      "awslogs-stream-prefix" = "ecs"
    }
  }
}
