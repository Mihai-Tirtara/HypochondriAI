# CloudWatch Log Group for Backend Application
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.project_name}-${var.environment}/backend"
  retention_in_days = var.log_retention_days

  kms_key_id = aws_kms_key.ecs.arn

  tags = {
    Name        = "${var.project_name}-${var.environment}-backend-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudWatch Log Group for ECS Execute Command
resource "aws_cloudwatch_log_group" "ecs_exec" {
  name              = "/ecs/${var.project_name}-${var.environment}/exec"
  retention_in_days = 7

  kms_key_id = aws_kms_key.ecs.arn

  tags = {
    Name        = "${var.project_name}-${var.environment}-ecs-exec-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "backend_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-backend-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ECS backend CPU utilization"
  alarm_actions       = []

  dimensions = {
    ServiceName = aws_ecs_service.backend.name
    ClusterName = aws_ecs_cluster.main.name
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-backend-cpu-high"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_cloudwatch_metric_alarm" "backend_memory_high" {
  alarm_name          = "${var.project_name}-${var.environment}-backend-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors ECS backend memory utilization"
  alarm_actions       = []

  dimensions = {
    ServiceName = aws_ecs_service.backend.name
    ClusterName = aws_ecs_cluster.main.name
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-backend-memory-high"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_cloudwatch_metric_alarm" "backend_task_count_low" {
  alarm_name          = "${var.project_name}-${var.environment}-backend-task-count-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "RunningTaskCount"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "This metric monitors ECS backend running task count"
  alarm_actions       = []

  dimensions = {
    ServiceName = aws_ecs_service.backend.name
    ClusterName = aws_ecs_cluster.main.name
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-backend-task-count-low"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "ecs_dashboard" {
  dashboard_name = "${var.project_name}-${var.environment}-ecs"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", aws_ecs_service.backend.name, "ClusterName", aws_ecs_cluster.main.name],
            [".", "MemoryUtilization", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "ECS Backend Resource Utilization"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "RunningTaskCount", "ServiceName", aws_ecs_service.backend.name, "ClusterName", aws_ecs_cluster.main.name],
            [".", "PendingTaskCount", ".", ".", ".", "."],
            [".", "DesiredCount", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "ECS Backend Task Counts"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6

        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.backend.name}' | fields @timestamp, @message | sort @timestamp desc | limit 100"
          region  = var.aws_region
          title   = "Recent Backend Logs"
          view    = "table"
        }
      }
    ]
  })
}
