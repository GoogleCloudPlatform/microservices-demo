# Enable APIs
module "enable_google_apis" {
  source                      = "terraform-google-modules/project-factory/google//modules/project_services"
  version                     = "~> 13.0"

  project_id                  = var.gcp_project_id
  disable_services_on_destroy = false

  activate_apis               = var.apis
}

# Create GKE Cluster
resource "google_container_cluster" "cluster" {
  name               = var.name
  location           = var.region
  ip_allocation_policy {
  }

  # Enabling Autopilot for this cluster
  enable_autopilot = true

  depends_on = [
    module.enable_google_apis
  ]
}

# Get Credentials for Cluster
resource "null_resource" "get_credentials" {
    provisioner "local-exec" {
        interpreter = ["bash", "-exc"]
        command     = "gcloud container clusters get-credentials ${var.name} --project=${var.gcp_project_id} --region=${var.region}"
    }

    depends_on = [
      resource.google_container_cluster.cluster
    ]
}

# Apply YAML kubernetes-manifest configurations
resource "null_resource" "apply_deployment" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = "kubectl apply -f ${var.filepath_manifest}"
  }

  depends_on = [
      resource.null_resource.get_credentials
  ]
}

# Wait condition for all Pods to be ready before finishing
resource "null_resource" "wait_conditions" {
    provisioner "local-exec" {
        interpreter = ["bash", "-exc"]
        command     = "kubectl wait --for=condition=ready pods --all -n ${var.namespace} --timeout=-1s"
    }

    depends_on = [
        resource.null_resource.apply_deployment
    ]
}