output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.app.arn
}

output "target_group_name" {
  description = "Name of the target group"
  value       = aws_lb_target_group.app.name
}

output "alb_listener_arn" {
  description = "ARN of the HTTPS listener"
  value       = var.domain_name != null || var.certificate_arn != null ? aws_lb_listener.https[0].arn : null
}

output "http_listener_arn" {
  description = "ARN of the HTTP listener"
  value       = aws_lb_listener.http.arn
}

output "access_logs_bucket_id" {
  description = "ID of the S3 bucket for access logs"
  value       = var.enable_access_logs ? aws_s3_bucket.alb_logs[0].id : null
}

output "certificate_arn" {
  description = "ARN of the SSL certificate"
  value       = var.domain_name != null ? aws_acm_certificate.main[0].arn : var.certificate_arn
}
