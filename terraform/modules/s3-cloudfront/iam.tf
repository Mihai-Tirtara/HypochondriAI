# IAM policy document for S3 deployment permissions
data "aws_iam_policy_document" "s3_deployment" {
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:PutObjectAcl",
      "s3:GetObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.frontend.arn,
      "${aws_s3_bucket.frontend.arn}/*"
    ]
  }
}

# IAM policy document for CloudFront invalidation permissions
data "aws_iam_policy_document" "cloudfront_invalidation" {
  statement {
    effect = "Allow"
    actions = [
      "cloudfront:CreateInvalidation",
      "cloudfront:GetInvalidation",
      "cloudfront:ListInvalidations"
    ]
    resources = [
      aws_cloudfront_distribution.frontend.arn
    ]
  }
}

# IAM policy for S3 deployment
resource "aws_iam_policy" "s3_deployment" {
  name        = "${var.project_name}-${var.environment}-s3-deployment"
  description = "Policy for deploying frontend assets to S3 bucket"
  policy      = data.aws_iam_policy_document.s3_deployment.json

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-s3-deployment-policy"
    Environment = var.environment
    Project     = var.project_name
  })
}

# IAM policy for CloudFront invalidation
resource "aws_iam_policy" "cloudfront_invalidation" {
  name        = "${var.project_name}-${var.environment}-cloudfront-invalidation"
  description = "Policy for creating CloudFront invalidations"
  policy      = data.aws_iam_policy_document.cloudfront_invalidation.json

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-cloudfront-invalidation-policy"
    Environment = var.environment
    Project     = var.project_name
  })
}

# Combined policy document for deployment user
data "aws_iam_policy_document" "deployment_combined" {
  source_policy_documents = [
    data.aws_iam_policy_document.s3_deployment.json,
    data.aws_iam_policy_document.cloudfront_invalidation.json
  ]
}

# IAM user for deployment (optional, for CI/CD)
resource "aws_iam_user" "deployment" {
  count = var.create_deployment_user ? 1 : 0
  name  = "${var.project_name}-${var.environment}-frontend-deployment"

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-frontend-deployment-user"
    Environment = var.environment
    Project     = var.project_name
  })
}

# Attach policies to deployment user
resource "aws_iam_user_policy_attachment" "deployment_s3" {
  count      = var.create_deployment_user ? 1 : 0
  user       = aws_iam_user.deployment[0].name
  policy_arn = aws_iam_policy.s3_deployment.arn
}

resource "aws_iam_user_policy_attachment" "deployment_cloudfront" {
  count      = var.create_deployment_user ? 1 : 0
  user       = aws_iam_user.deployment[0].name
  policy_arn = aws_iam_policy.cloudfront_invalidation.arn
}

# Access keys for deployment user (optional)
resource "aws_iam_access_key" "deployment" {
  count = var.create_deployment_user && var.create_access_keys ? 1 : 0
  user  = aws_iam_user.deployment[0].name
}

# Store access keys in AWS Secrets Manager (optional)
resource "aws_secretsmanager_secret" "deployment_access_key" {
  count                   = var.create_deployment_user && var.create_access_keys && var.store_keys_in_secrets_manager ? 1 : 0
  name                    = "${var.project_name}/${var.environment}/frontend/deployment-access-key"
  description             = "Access key for frontend deployment user"
  force_overwrite_replica_secret = true

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-deployment-access-key-secret"
    Environment = var.environment
    Project     = var.project_name
  })
}

resource "aws_secretsmanager_secret_version" "deployment_access_key" {
  count     = var.create_deployment_user && var.create_access_keys && var.store_keys_in_secrets_manager ? 1 : 0
  secret_id = aws_secretsmanager_secret.deployment_access_key[0].id
  secret_string = jsonencode({
    access_key_id     = aws_iam_access_key.deployment[0].id
    secret_access_key = aws_iam_access_key.deployment[0].secret
  })
}

resource "aws_secretsmanager_secret" "deployment_secret_key" {
  count                   = var.create_deployment_user && var.create_access_keys && var.store_keys_in_secrets_manager ? 1 : 0
  name                    = "${var.project_name}/${var.environment}/frontend/deployment-secret-key"
  description             = "Secret key for frontend deployment user"
  force_overwrite_replica_secret = true

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.environment}-deployment-secret-key-secret"
    Environment = var.environment
    Project     = var.project_name
  })
}

resource "aws_secretsmanager_secret_version" "deployment_secret_key" {
  count     = var.create_deployment_user && var.create_access_keys && var.store_keys_in_secrets_manager ? 1 : 0
  secret_id = aws_secretsmanager_secret.deployment_secret_key[0].id
  secret_string = aws_iam_access_key.deployment[0].secret
}
