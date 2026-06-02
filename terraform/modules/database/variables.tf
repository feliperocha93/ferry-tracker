variable "project_name" {
  description = "Neon project name."
  type        = string
}

variable "org_id" {
  description = "Neon organization ID (Account settings → Organization settings)."
  type        = string
}

variable "region_id" {
  description = "Neon region (e.g. aws-sa-east-1 for São Paulo)."
  type        = string
}

variable "pg_version" {
  description = "PostgreSQL major version."
  type        = number
  default     = 16
}

variable "branch_name" {
  description = "Primary branch name."
  type        = string
  default     = "main"
}

variable "database_name" {
  description = "Application database name."
  type        = string
}

variable "role_name" {
  description = "Database owner role name."
  type        = string
}

variable "history_retention_seconds" {
  description = "Point-in-time recovery window. Free tier max: 21600 (6 hours)."
  type        = number
  default     = 21600
}

variable "autoscaling_limit_min_cu" {
  description = "Minimum compute units for the default endpoint."
  type        = number
  default     = 0.25
}

variable "autoscaling_limit_max_cu" {
  description = "Maximum compute units for the default endpoint."
  type        = number
  default     = 1
}
