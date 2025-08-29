# Required variables
variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., prod, staging, dev)"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the DB subnet group"
  type        = list(string)
  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "At least 2 subnet IDs are required for RDS subnet group."
  }
}

variable "rds_security_group_id" {
  description = "Security group ID for RDS instance"
  type        = string
}

# Instance configuration
variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
  validation {
    condition     = can(regex("^db\\.(t3|t4g|m5|m6i|r5|r6i)\\.", var.instance_class))
    error_message = "Instance class must be a valid RDS instance type (e.g., db.t3.micro, db.m5.large)."
  }
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.8"
  validation {
    condition     = can(regex("^1[5-9]\\.", var.engine_version))
    error_message = "Engine version must be PostgreSQL 15 or higher."
  }
}

# Storage configuration
variable "allocated_storage" {
  description = "Initial amount of storage (GB)"
  type        = number
  default     = 20
  validation {
    condition     = var.allocated_storage >= 20 && var.allocated_storage <= 65536
    error_message = "Allocated storage must be between 20 GB and 65536 GB."
  }
}

variable "max_allocated_storage" {
  description = "Maximum amount of storage (GB) for autoscaling"
  type        = number
  default     = 100
  validation {
    condition     = var.max_allocated_storage >= 20
    error_message = "Max allocated storage must be at least 20 GB."
  }
}

variable "storage_type" {
  description = "Storage type"
  type        = string
  default     = "gp3"
  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2"], var.storage_type)
    error_message = "Storage type must be gp2, gp3, io1, or io2."
  }
}

# High availability
variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = true
}

variable "availability_zone" {
  description = "Availability zone for single-AZ deployment"
  type        = string
  default     = null
}

# Backup configuration
variable "backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
  validation {
    condition     = var.backup_retention_period >= 1 && var.backup_retention_period <= 35
    error_message = "Backup retention period must be between 1 and 35 days."
  }
}

variable "backup_window" {
  description = "Backup window in UTC"
  type        = string
  default     = "02:00-04:00"
  validation {
    condition     = can(regex("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]-([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", var.backup_window))
    error_message = "Backup window must be in format HH:MM-HH:MM (e.g., 02:00-04:00)."
  }
}

# Maintenance configuration
variable "maintenance_window" {
  description = "Maintenance window"
  type        = string
  default     = "sun:04:30-sun:05:30"
  validation {
    condition     = can(regex("^(mon|tue|wed|thu|fri|sat|sun):[0-2][0-9]:[0-5][0-9]-(mon|tue|wed|thu|fri|sat|sun):[0-2][0-9]:[0-5][0-9]$", var.maintenance_window))
    error_message = "Maintenance window must be in format ddd:HH:MM-ddd:HH:MM (e.g., sun:03:00-sun:04:00)."
  }
}

# Monitoring configuration
variable "performance_insights_enabled" {
  description = "Enable Performance Insights"
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "Performance Insights retention period in days"
  type        = number
  default     = 7
  validation {
    condition     = contains([7, 731], var.performance_insights_retention_period)
    error_message = "Performance Insights retention period must be 7 (free) or 731 days (paid)."
  }
}

variable "monitoring_interval" {
  description = "Enhanced monitoring interval in seconds (0 to disable)"
  type        = number
  default     = 60
  validation {
    condition     = contains([0, 1, 5, 10, 15, 30, 60], var.monitoring_interval)
    error_message = "Monitoring interval must be 0, 1, 5, 10, 15, 30, or 60 seconds."
  }
}

variable "enabled_cloudwatch_logs_exports" {
  description = "List of log types to export to CloudWatch"
  type        = list(string)
  default     = ["postgresql"]
  validation {
    condition     = alltrue([for log_type in var.enabled_cloudwatch_logs_exports : contains(["postgresql", "upgrade"], log_type)])
    error_message = "Log types must be from: postgresql, upgrade."
  }
}
