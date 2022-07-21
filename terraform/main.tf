# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

locals {
  apis = [
    "container.googleapis.com",
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
    "clouddebugger.googleapis.com",
    "cloudprofiler.googleapis.com"
  ]
}

# Enable Google Cloud APIs
module "enable_google_apis" {
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "~> 13.0"

  project_id                  = var.gcp_project_id
  disable_services_on_destroy = false

  activate_apis = local.apis
}

# Create GKE cluster
resource "google_container_cluster" "my_cluster" {
  name     = var.name
  location = var.region

  # Enabling autopilot for this cluster
  enable_autopilot = true

  # Setting an empty ip_allocation_policy to allow autopilot cluster to spin up correctly
  ip_allocation_policy {
  }

  depends_on = [
    module.enable_google_apis
  ]
}

# Authorization for the GKE cluster
module "gke_auth" {
  source = "terraform-google-modules/kubernetes-engine/google//modules/auth"

  project_id   = var.gcp_project_id
  cluster_name = var.name
  location     = var.region

  depends_on = [
    google_container_cluster.my_cluster
  ]
}

# Apply YAML kubernetes-manifest configurations
resource "null_resource" "apply_deployment" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = "kubectl apply -f ${var.filepath_manifest}"
  }

  depends_on = [
    module.gke_auth
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
