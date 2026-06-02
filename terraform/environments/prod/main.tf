module "database" {
  source = "../../modules/database"

  project_name  = var.project_name
  org_id        = var.neon_org_id
  region_id     = var.region_id
  pg_version    = var.pg_version
  database_name = var.database_name
  role_name     = var.role_name
}
