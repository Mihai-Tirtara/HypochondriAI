variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "default_cache_ttl" {
  description = "Default TTL for CloudFront cache in seconds"
  type        = number
  default     = 86400 # 24 hours
}

variable "max_cache_ttl" {
  description = "Maximum TTL for CloudFront cache in seconds"
  type        = number
  default     = 31536000 # 1 year
}

variable "static_cache_ttl" {
  description = "TTL for static assets (CSS, JS, images) in seconds"
  type        = number
  default     = 31536000 # 1 year
}

variable "price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
  validation {
    condition = contains([
      "PriceClass_All",
      "PriceClass_200",
      "PriceClass_100"
    ], var.price_class)
    error_message = "Price class must be one of: PriceClass_All, PriceClass_200, PriceClass_100."
  }
}

variable "custom_domain" {
  description = "Custom domain name for CloudFront distribution (optional)"
  type        = string
  default     = null
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for custom domain (required if custom_domain is set)"
  type        = string
  default     = null
}

variable "enable_ipv6" {
  description = "Enable IPv6 for CloudFront distribution"
  type        = bool
  default     = true
}

variable "web_acl_id" {
  description = "AWS WAF web ACL ID to associate with CloudFront distribution (optional)"
  type        = string
  default     = null
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "create_deployment_user" {
  description = "Create IAM user for deployment"
  type        = bool
  default     = false
}

variable "create_access_keys" {
  description = "Create access keys for deployment user (requires create_deployment_user = true)"
  type        = bool
  default     = false
}

variable "store_keys_in_secrets_manager" {
  description = "Store access keys in AWS Secrets Manager (requires create_access_keys = true)"
  type        = bool
  default     = false
}
