module "gke" {
  source = "../../modules/gke"

  project_id   = var.project_id
  name         = var.name
  region       = var.region
  enable_apis  = var.enable_apis
  memorystore  = var.memorystore
}
