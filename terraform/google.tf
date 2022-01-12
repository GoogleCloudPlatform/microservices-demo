# Copyright 2022 Paulo Albuquerque
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

# Set Google provider defaults
provider "google" {
  project = var.project_id
  region  = var.region
}

# Activate the necessary GCP APIs
resource "google_project_service" "gcp_apis" {
  for_each                   = toset(["cloudresourcemanager.googleapis.com", "compute.googleapis.com", "container.googleapis.com", "servicenetworking.googleapis.com"])
  project                    = var.project_id
  service                    = each.value
  disable_dependent_services = false
  disable_on_destroy         = false
}
