# Auto Scaling Target
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  # Tags removed due to IAM permission issues with application-autoscaling:TagResource
  # tags = {
  #   Name        = "${var.project_name}-${var.environment}-ecs-scaling-target"
  #   Environment = var.environment
  #   Project     = var.project_name
  # }
}

# Auto Scaling Policy - CPU Utilization
resource "aws_appautoscaling_policy" "ecs_cpu_policy" {
  name               = "${var.project_name}-${var.environment}-ecs-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = var.cpu_target_value
    disable_scale_in   = false
    scale_in_cooldown  = var.scale_down_cooldown
    scale_out_cooldown = var.scale_up_cooldown

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

# Auto Scaling Policy - Memory Utilization
resource "aws_appautoscaling_policy" "ecs_memory_policy" {
  name               = "${var.project_name}-${var.environment}-ecs-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = var.memory_target_value
    disable_scale_in   = false
    scale_in_cooldown  = var.scale_down_cooldown
    scale_out_cooldown = var.scale_up_cooldown

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
  }
}

# Auto Scaling Policy - ALB Request Count (disabled due to dependency issues)
# This policy can be re-enabled once the ALB and target group are stable
# resource "aws_appautoscaling_policy" "ecs_request_count_policy" {
#   name               = "${var.project_name}-${var.environment}-ecs-request-count-scaling"
#   policy_type        = "TargetTrackingScaling"
#   resource_id        = aws_appautoscaling_target.ecs_target.resource_id
#   scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
#   service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
#
#   target_tracking_scaling_policy_configuration {
#     target_value       = 200 # Target 200 requests per minute per target
#     disable_scale_in   = false
#     scale_in_cooldown  = var.scale_down_cooldown
#     scale_out_cooldown = var.scale_up_cooldown
#
#     predefined_metric_specification {
#       predefined_metric_type = "ALBRequestCountPerTarget"
#       resource_label         = "${local.alb_resource_label}/${local.target_group_resource_label}"
#     }
#   }
# }
