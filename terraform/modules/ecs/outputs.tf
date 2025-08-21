output "cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "service_arn" {
  description = "ARN of the ECS service"
  value       = aws_ecs_service.backend.id
}

output "service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.backend.name
}

output "task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = aws_ecs_task_definition.backend.arn
}

output "task_definition_family" {
  description = "Family of the ECS task definition"
  value       = aws_ecs_task_definition.backend.family
}

output "task_definition_revision" {
  description = "Revision of the ECS task definition"
  value       = aws_ecs_task_definition.backend.revision
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_repository_name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.backend.name
}

output "ecr_repository_arn" {
  description = "ARN of the ECR repository"
  value       = aws_ecr_repository.backend.arn
}

output "backend_log_group_name" {
  description = "Name of the backend CloudWatch log group"
  value       = aws_cloudwatch_log_group.backend.name
}

output "backend_log_group_arn" {
  description = "ARN of the backend CloudWatch log group"
  value       = aws_cloudwatch_log_group.backend.arn
}

output "ecs_execution_role_arn" {
  description = "ARN of the ECS execution role"
  value       = aws_iam_role.ecs_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task_role.arn
}

output "kms_key_arn" {
  description = "ARN of the KMS key used for ECS encryption"
  value       = aws_kms_key.ecs.arn
}

output "autoscaling_target_arn" {
  description = "ARN of the Auto Scaling target"
  value       = aws_appautoscaling_target.ecs_target.arn
}
