variable "neon_org_id" {
  description = "Neon organization ID."
  type        = string
}

variable "project_name" {
  description = "Neon project name."
  type        = string
  default     = "ferry-wait"
}

variable "region_id" {
  description = "Neon region."
  type        = string
  default     = "aws-sa-east-1"
}

variable "pg_version" {
  description = "PostgreSQL major version."
  type        = number
  default     = 16
}

variable "database_name" {
  description = "Application database name."
  type        = string
  default     = "ferry_wait"
}

variable "role_name" {
  description = "Database owner role name."
  type        = string
  default     = "ferry"
}
