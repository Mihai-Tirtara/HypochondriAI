output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.frontend.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.frontend.arn
}

output "s3_bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.frontend.bucket_domain_name
}

output "s3_bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket"
  value       = aws_s3_bucket.frontend.bucket_regional_domain_name
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.arn
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "cloudfront_hosted_zone_id" {
  description = "Hosted zone ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.hosted_zone_id
}

output "cloudfront_distribution_status" {
  description = "Current status of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.status
}

output "origin_access_control_id" {
  description = "ID of the Origin Access Control"
  value       = aws_cloudfront_origin_access_control.frontend.id
}

output "website_url" {
  description = "URL of the website"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "response_headers_policy_id" {
  description = "ID of the CloudFront response headers policy"
  value       = aws_cloudfront_response_headers_policy.frontend.id
}

# IAM outputs
output "s3_deployment_policy_arn" {
  description = "ARN of the S3 deployment policy"
  value       = aws_iam_policy.s3_deployment.arn
}

output "cloudfront_invalidation_policy_arn" {
  description = "ARN of the CloudFront invalidation policy"
  value       = aws_iam_policy.cloudfront_invalidation.arn
}

output "deployment_user_arn" {
  description = "ARN of the deployment IAM user (if created)"
  value       = var.create_deployment_user ? aws_iam_user.deployment[0].arn : null
}

output "deployment_user_name" {
  description = "Name of the deployment IAM user (if created)"
  value       = var.create_deployment_user ? aws_iam_user.deployment[0].name : null
}

output "deployment_access_key_id" {
  description = "Access key ID for deployment user (if created)"
  value       = var.create_deployment_user && var.create_access_keys ? aws_iam_access_key.deployment[0].id : null
  sensitive   = true
}

output "deployment_secret_access_key" {
  description = "Secret access key for deployment user (if created)"
  value       = var.create_deployment_user && var.create_access_keys ? aws_iam_access_key.deployment[0].secret : null
  sensitive   = true
}
