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

# Get deployment manifests
data "kubectl_path_documents" "manifests" {
  pattern          = "${path.module}/../release/kubernetes-manifests.yaml"
  disable_template = true
}

# Retrieve an access token as the Terraform runner
data "google_client_config" "provider" {}

# Authenticate to the GKE cluster
provider "kubectl" {
  load_config_file       = false
  host                   = "https://${google_container_cluster.primary.endpoint}"
  token                  = data.google_client_config.provider.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth.0.cluster_ca_certificate)
}

# Apply the application manifests
resource "kubectl_manifest" "application" {
  for_each  = toset(data.kubectl_path_documents.manifests.documents)
  yaml_body = each.value
}
