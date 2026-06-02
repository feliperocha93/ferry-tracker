output "project_id" {
  description = "Neon project ID."
  value       = module.database.project_id
}

output "project_name" {
  description = "Neon project name."
  value       = module.database.project_name
}

output "branch_id" {
  description = "Default branch ID."
  value       = module.database.branch_id
}

output "database_name" {
  description = "Application database name."
  value       = module.database.database_name
}

output "role_name" {
  description = "Database owner role name."
  value       = module.database.role_name
}

output "database_url" {
  description = "Neon connection URI. Store as GitHub Secret DATABASE_URL (use database_url_sqlalchemy for the app)."
  value       = module.database.database_url
  sensitive   = true
}

output "database_url_sqlalchemy" {
  description = "SQLAlchemy connection string for ferry-wait (Alembic, crawler --save)."
  value       = module.database.database_url_sqlalchemy
  sensitive   = true
}
