/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

# Set defaults for the google Terraform provider.
provider "google" {
  project = var.project_id
  region  = "us-central1"
  zone    = "us-central1-a"
}

terraform {
  # Store the state inside a Google Cloud Storage bucket.
  backend "gcs" {
    bucket = "cicd-terraform-state"
    prefix = "terraform-state"
  }
}

# Enable Google Cloud APIs.
module "enable_google_apis" {
  source                      = "terraform-google-modules/project-factory/google//modules/project_services"
  version                     = "~> 17.0"
  disable_services_on_destroy = false
  activate_apis = [
    "cloudresourcemanager.googleapis.com",
    "container.googleapis.com",
    "iam.googleapis.com",
    "storage.googleapis.com",
  ]
  project_id = var.project_id
}

# Google Cloud Storage for storing Terraform state (.tfstate).
resource "google_storage_bucket" "terraform_state_storage_bucket" {
  name                        = "cicd-terraform-state"
  location                    = "us"
  storage_class               = "STANDARD"
  force_destroy               = false
  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}

# Google Cloud IAM service account for GKE clusters.
# We avoid using the Compute Engine default service account because it's too permissive.
resource "google_service_account" "gke_clusters_service_account" {
  account_id   = "gke-clusters-service-account"
  display_name = "My Service Account"
  depends_on = [
    module.enable_google_apis
  ]
}

# See https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster#use_least_privilege_sa
resource "google_project_iam_member" "gke_clusters_service_account_role_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke_clusters_service_account.email}"
}

# See https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster#use_least_privilege_sa
resource "google_project_iam_member" "gke_clusters_service_account_role_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke_clusters_service_account.email}"
}

# See https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster#use_least_privilege_sa
resource "google_project_iam_member" "gke_clusters_service_account_role_monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.gke_clusters_service_account.email}"
}

# See https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster#use_least_privilege_sa
resource "google_project_iam_member" "gke_clusters_service_account_role_stackdriver_writer" {
  project = var.project_id
  role    = "roles/stackdriver.resourceMetadata.writer"
  member  = "serviceAccount:${google_service_account.gke_clusters_service_account.email}"
}

# The GKE cluster used for pull-request (PR) staging deployments.
resource "google_container_cluster" "prs_gke_cluster" {
  name                = "prs-gke-cluster"
  location            = "us-central1"
  enable_autopilot    = true
  project             = var.project_id
  deletion_protection = true
  depends_on = [
    module.enable_google_apis
  ]
  cluster_autoscaling {
    auto_provisioning_defaults {
      service_account = google_service_account.gke_clusters_service_account.email
    }
  }
  # Need an empty ip_allocation_policy to overcome an error related to autopilot node pool constraints.
  # Workaround from https://github.com/hashicorp/terraform-provider-google/issues/10782#issuecomment-1024488630
  ip_allocation_policy {
  }
}
