data "terraform_remote_state" "cluster" {
  count   = var.use_remote_state ? 1 : 0
  backend = "gcs"

  config = {
    bucket = var.tfstate_bucket
    prefix = "state/cluster"
  }
}

locals {
  cluster_name   = var.use_remote_state ? data.terraform_remote_state.cluster[0].outputs.cluster_name : var.cluster_name
  region         = var.use_remote_state ? data.terraform_remote_state.cluster[0].outputs.cluster_location : var.region
  repo_root      = abspath("${path.module}/../../..")
  manifest_path  = "kustomize/overlays/production"
}

module "app_deploy" {
  source = "../../modules/app-deploy"

  project_id        = var.project_id
  cluster_name      = local.cluster_name
  region            = local.region
  namespace         = "production"
  filepath_manifest = local.manifest_path
  repo_root         = local.repo_root
}
