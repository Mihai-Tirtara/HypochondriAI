output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "vpc_endpoints_security_group_id" {
  description = "VPC endpoints security group ID"
  value       = module.vpc.vpc_endpoints_security_group_id
}

# ALB Outputs
output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = module.alb.alb_arn
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = module.alb.alb_zone_id
}

output "target_group_arn" {
  description = "ARN of the target group for ECS integration"
  value       = module.alb.target_group_arn
}

# RDS Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.rds_endpoint
}

output "rds_secret_arn" {
  description = "ARN of the RDS credentials secret"
  value       = module.rds.secret_arn
}

# ECR Outputs
output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = module.ecr.repository_url
}

output "ecr_repository_name" {
  description = "Name of the ECR repository"
  value       = module.ecr.repository_name
}

output "ecr_repository_arn" {
  description = "ARN of the ECR repository"
  value       = module.ecr.repository_arn
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = module.ecs.cluster_arn
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = module.ecs.service_name
}

output "ecs_service_arn" {
  description = "ARN of the ECS service"
  value       = module.ecs.service_arn
}


output "ecs_log_group_name" {
  description = "Name of the ECS CloudWatch log group"
  value       = module.ecs.backend_log_group_name
}

# S3 + CloudFront Outputs
output "frontend_s3_bucket_name" {
  description = "Name of the frontend S3 bucket"
  value       = module.s3_cloudfront.s3_bucket_name
}

output "frontend_cloudfront_distribution_id" {
  description = "ID of the frontend CloudFront distribution"
  value       = module.s3_cloudfront.cloudfront_distribution_id
}

output "frontend_cloudfront_domain_name" {
  description = "Domain name of the frontend CloudFront distribution"
  value       = module.s3_cloudfront.cloudfront_domain_name
}

output "frontend_website_url" {
  description = "URL of the frontend website"
  value       = module.s3_cloudfront.website_url
}

output "frontend_deployment_user_name" {
  description = "Name of the frontend deployment IAM user"
  value       = module.s3_cloudfront.deployment_user_name
}

output "frontend_deployment_access_key_id" {
  description = "Access key ID for frontend deployment user"
  value       = module.s3_cloudfront.deployment_access_key_id
  sensitive   = true
}

output "frontend_deployment_secret_access_key" {
  description = "Secret access key for frontend deployment user"
  value       = module.s3_cloudfront.deployment_secret_access_key
  sensitive   = true
}
