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

# Definition of local variables
locals {
  base_apis = [
    "container.googleapis.com",
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
    "clouddebugger.googleapis.com",
    "cloudprofiler.googleapis.com"
  ]
  memorystore_apis = ["redis.googleapis.com"]
  
  # Variables cluster_list and cluster_name are used for an implicit dependency
  # between module "gcloud" and resource "google_container_cluster" 
  cluster_id_parts = split("/", google_container_cluster.my_cluster.id)
  cluster_name = element(local.cluster_id_parts, length(local.cluster_id_parts) - 1)
}

# Enable Google Cloud APIs
module "enable_google_apis" {
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "~> 13.0"

  project_id                  = var.gcp_project_id
  disable_services_on_destroy = false

  # activate_apis is the set of base_apis and the APIs required by user-configured deployment options
  activate_apis = concat(local.base_apis, var.memorystore ? local.memorystore_apis : [])
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

# Get credentials for cluster
module "gcloud" {
  source  = "terraform-google-modules/gcloud/google"
  version = "~> 2.0"

  platform              = "linux"
  additional_components = ["kubectl", "beta"]

  create_cmd_entrypoint = "gcloud"
  # Use local variable cluster_name for an implicit dependency on resource "google_container_cluster" 
  create_cmd_body = "container clusters get-credentials ${local.cluster_name} --zone=${var.region}"
}

# Apply YAML kubernetes-manifest configurations
resource "null_resource" "apply_deployment" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = "kubectl apply -f ${var.filepath_manifest}"
  }

  depends_on = [
    module.gcloud
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
