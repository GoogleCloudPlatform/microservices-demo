locals {
  base_apis = [
    "container.googleapis.com",
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
    "cloudprofiler.googleapis.com",
  ]
  memorystore_apis = ["redis.googleapis.com"]
}

module "enable_google_apis" {
  count   = var.enable_apis ? 1 : 0
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "~> 18.0"

  project_id                  = var.project_id
  disable_services_on_destroy  = false
  activate_apis                = concat(local.base_apis, var.memorystore ? local.memorystore_apis : [])
}

resource "google_container_cluster" "main" {
  name     = var.name
  location = var.region

  enable_autopilot    = true
  deletion_protection = false
  ip_allocation_policy {}

  depends_on = [module.enable_google_apis]
}
