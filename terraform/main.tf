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
    "cloudprofiler.googleapis.com"
  ]
  memorystore_apis = ["redis.googleapis.com"]
  cluster_name     = var.enable_autopilot == true ? google_container_cluster.my_autopilot_cluster[0].name : google_container_cluster.my_cluster[0].name
}

# Enable Google Cloud APIs
module "enable_google_apis" {
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "~> 14.0"

  project_id                  = var.gcp_project_id
  disable_services_on_destroy = false

  # activate_apis is the set of base_apis and the APIs required by user-configured deployment options
  activate_apis = concat(local.base_apis, var.memorystore ? local.memorystore_apis : [])
}

# Create GKE cluster
resource "google_container_cluster" "my_autopilot_cluster" {
  count = var.enable_autopilot == true ? 1 : 0

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

# TODO: merge my_autopilot_cluster and my_cluster resource into one after
# fixing https://github.com/hashicorp/terraform-provider-google/issues/13857
resource "google_container_cluster" "my_cluster" {
  count = var.enable_autopilot == false && var.gke_node_pool != null ? 1 : 0

  name     = var.name
  location = var.region

  node_pool {
    node_config {
      machine_type = var.gke_node_pool.machine_type
      oauth_scopes = var.gke_node_pool.oauth_scopes
      labels       = var.gke_node_pool.labels
    }

    initial_node_count = var.gke_node_pool.initial_node_count

    autoscaling {
      min_node_count = var.gke_node_pool.autoscaling.min_node_count
      max_node_count = var.gke_node_pool.autoscaling.max_node_count
    }
  }

  depends_on = [
    module.enable_google_apis
  ]
}

# Get credentials for cluster
module "gcloud" {
  source  = "terraform-google-modules/gcloud/google"
  version = "~> 3.0"

  platform              = "linux"
  additional_components = ["kubectl", "beta"]

  create_cmd_entrypoint = "gcloud"
  # Module does not support explicit dependency
  # Enforce implicit dependency through use of local variable
  create_cmd_body = "container clusters get-credentials ${local.cluster_name} --zone=${var.region} --project=${var.gcp_project_id}"
}

# Apply YAML kubernetes-manifest configurations
resource "null_resource" "apply_deployment" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = "kubectl apply -k ${var.filepath_manifest}"
  }

  depends_on = [
    module.gcloud
  ]
}

# Wait condition for all Pods to be ready before finishing
resource "null_resource" "wait_conditions" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = "kubectl wait --for=condition=ready pods --all -n ${var.namespace} --timeout=-1s 2> /dev/null"
  }

  depends_on = [
    resource.null_resource.apply_deployment
  ]
}
