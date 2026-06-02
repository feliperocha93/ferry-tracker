resource "neon_project" "this" {
  name                      = var.project_name
  org_id                    = var.org_id
  region_id                 = var.region_id
  pg_version                = var.pg_version
  history_retention_seconds = var.history_retention_seconds

  branch {
    name          = var.branch_name
    database_name = var.database_name
    role_name     = var.role_name
  }

  default_endpoint_settings {
    autoscaling_limit_min_cu = var.autoscaling_limit_min_cu
    autoscaling_limit_max_cu = var.autoscaling_limit_max_cu
  }
}
