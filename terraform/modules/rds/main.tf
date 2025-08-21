# Random password for RDS master user
resource "random_password" "master" {
  length           = 16
  special          = true
  # Avoid characters that commonly break RDS master passwords
  override_special = "!#$%^*-_=+[]{}:,.?"   # omit / @ ' " \ & < > ( ) ; space
  min_lower        = 1
  min_upper        = 1
  min_numeric      = 1
  min_special      = 1
}

# Secrets Manager secret for RDS credentials
resource "aws_secretsmanager_secret" "rds_credentials" {
  name                    = "${var.project_name}/${var.environment}/rds/master"
  description             = "RDS master user credentials"
  recovery_window_in_days = 7

  tags = {
    Name        = "${var.project_name}-rds-secret"
    Environment = var.environment
  }
}

# Secrets Manager secret version
resource "aws_secretsmanager_secret_version" "rds_credentials" {
  secret_id = aws_secretsmanager_secret.rds_credentials.id
  secret_string = jsonencode({
    username = "postgres"
    password = random_password.master.result
  })
}

# DB subnet group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name        = "${var.project_name}-db-subnet-group"
    Environment = var.environment
  }
}

# DB parameter group
resource "aws_db_parameter_group" "main" {
  family = "postgres15"
  name   = "${var.project_name}-${var.environment}-postgres15"

  # Performance optimizations for db.t3.micro (1GB RAM)
  parameter {
    name  = "shared_buffers"
    value = "32768"  # 256MB in 8KB pages
  }

  parameter {
    name  = "effective_cache_size"
    value = "98304"   # 768MB in 8KB pages
  }

  parameter {
    name  = "work_mem"
    value = "4096"    # 4MB in KB
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "65536"   # 64MB in KB
  }

  parameter {
    name  = "max_connections"
    value = "50"
  }

  # Storage optimizations for SSD/gp3
  parameter {
    name  = "random_page_cost"
    value = "1.1"
  }

  parameter {
    name  = "checkpoint_completion_target"
    value = "0.9"
  }

  parameter {
    name  = "wal_buffers"
    value = "2048"    # 16MB in 8KB pages
  }

  # Logging and monitoring
  parameter {
    name  = "log_statement"
    value = "ddl"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"    # Log queries > 1 second
  }

  parameter {
    name  = "log_checkpoints"
    value = "on"
  }

  tags = {
    Name        = "${var.project_name}-postgres15-params"
    Environment = var.environment
  }
}

# RDS instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-db"

  # Engine configuration
  engine               = "postgres"
  engine_version       = var.engine_version
  instance_class       = var.instance_class

  # Storage configuration
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type         = var.storage_type
  storage_encrypted    = true

  # Database configuration
  db_name  = "hypochondriai"
  username = "postgres"
  manage_master_user_password = true

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.rds_security_group_id]
  publicly_accessible    = false

  # High availability
  multi_az               = var.multi_az
  availability_zone      = var.multi_az ? null : var.availability_zone

  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  delete_automated_backups = false
  final_snapshot_identifier = "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  skip_final_snapshot    = false
  copy_tags_to_snapshot  = true

  # Maintenance configuration
  maintenance_window         = var.maintenance_window
  auto_minor_version_upgrade = false
  apply_immediately         = false

  # Monitoring configuration
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_retention_period
  monitoring_interval                   = var.monitoring_interval
  monitoring_role_arn                  = var.monitoring_interval > 0 ? aws_iam_role.rds_monitoring[0].arn : null
  enabled_cloudwatch_logs_exports      = var.enabled_cloudwatch_logs_exports

  # Parameter group
  parameter_group_name = aws_db_parameter_group.main.name

  tags = {
    Name        = "${var.project_name}-${var.environment}-db"
    Environment = var.environment
  }

  depends_on = [
    aws_secretsmanager_secret_version.rds_credentials
  ]
}

# IAM role for RDS enhanced monitoring
resource "aws_iam_role" "rds_monitoring" {
  count = var.monitoring_interval > 0 ? 1 : 0
  name  = "${var.project_name}-${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-rds-monitoring-role"
    Environment = var.environment
  }
}

# Attach AWS managed policy for RDS enhanced monitoring
resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count      = var.monitoring_interval > 0 ? 1 : 0
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Database URL Secret for Application
resource "aws_secretsmanager_secret" "database_url" {
  name                    = "${var.project_name}/${var.environment}/rds/database-url"
  description             = "Database URL for application connection"
  recovery_window_in_days = 7

  tags = {
    Name        = "${var.project_name}-database-url-secret"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = aws_secretsmanager_secret.database_url.id
  secret_string = "postgresql://postgres:${random_password.master.result}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
}
