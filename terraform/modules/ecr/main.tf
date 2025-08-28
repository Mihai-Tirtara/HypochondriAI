# ECR Repository
resource "aws_ecr_repository" "this" {
  name                 = "${var.project_name}/${var.repository_name}"
  image_tag_mutability = var.image_tag_mutability
  force_delete        = var.force_delete

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  encryption_configuration {
    encryption_type = var.encryption_type
    kms_key         = var.kms_key
  }

  tags = merge(
    {
      Name        = "${var.project_name}-${var.repository_name}-ecr"
      Environment = var.environment
      Project     = var.project_name
    },
    var.tags
  )
}

# ECR Lifecycle Policy
resource "aws_ecr_lifecycle_policy" "this" {
  repository = aws_ecr_repository.this.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last ${var.lifecycle_policy.keep_last_images} images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = var.lifecycle_policy.keep_last_images
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than ${var.lifecycle_policy.untagged_days} day(s)"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = var.lifecycle_policy.untagged_days
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
