output "project_id" {
  description = "Neon project ID."
  value       = neon_project.this.id
}

output "project_name" {
  description = "Neon project name."
  value       = neon_project.this.name
}

output "branch_id" {
  description = "Default branch ID."
  value       = neon_project.this.default_branch_id
}

output "database_name" {
  description = "Application database name."
  value       = var.database_name
}

output "role_name" {
  description = "Database owner role name."
  value       = var.role_name
}

output "database_url" {
  description = "Neon connection URI (postgresql://…)."
  value       = neon_project.this.connection_uri
  sensitive   = true
}

output "database_url_sqlalchemy" {
  description = "SQLAlchemy/psycopg connection string for ferry-wait (postgresql+psycopg://…)."
  value       = replace(neon_project.this.connection_uri, "postgresql://", "postgresql+psycopg://")
  sensitive   = true
}
