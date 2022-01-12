# Copyright 2021 Paulo Albuquerque
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

output "region" {
  value       = var.region
  description = "Google Cloud Region"
}

output "project_id" {
  value       = var.project_id
  description = "Google Cloud Project ID"
}

output "kubernetes_cluster_name" {
  value       = google_container_cluster.primary.name
  description = "GKE Cluster Name"
}

output "kubernetes_cluster_host" {
  value       = google_container_cluster.primary.endpoint
  description = "GKE Cluster Host"
}

output "instructions" {
  value       = <<EOF
  Run the following commands to retrieve the endpoint for the application:
  gcloud container clusters get-credentials ${var.app_name} --zone ${var.region} --project ${var.project_id}
  kubectl get service frontend-external | awk '{print $4}'
  EOF
  description = "Instructions for retrieving the endpoint for the application"
}
