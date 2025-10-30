# accounting.tf - GCP Accounting Service Cloud Run Infrastructure with VPC Connector

# Enable necessary APIs
resource "google_project_service" "accounting_apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "vpcaccess.googleapis.com",
    "compute.googleapis.com"
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# Create Artifact Registry repository for accounting service
resource "google_artifact_registry_repository" "accounting_repo" {
  location      = "us-central1"
  repository_id = "accounting-repo"
  description   = "Docker repository for accounting service"
  format        = "DOCKER"
  project       = var.project_id

  depends_on = [google_project_service.accounting_apis]
}

# Reference to the CRM VPC network
data "google_compute_network" "crm_vpc" {
  name    = "crm-vpc"
  project = var.project_id
}

# Create VPC Connector for accessing CRM service
# Note: VPC Connector uses a dedicated /28 subnet (16 IPs)
resource "google_vpc_access_connector" "accounting_connector" {
  name          = "accounting-connector"
  region        = "us-central1"
  network       = data.google_compute_network.crm_vpc.name
  ip_cidr_range = "10.3.1.0/28"  # Dedicated range for connector (16 IPs)
  
  # Connector throughput settings
  min_throughput = 200  # Minimum 200 Mbps
  max_throughput = 1000  # Maximum 1000 Mbps
  
  project = var.project_id

  depends_on = [google_project_service.accounting_apis]
}

# Firewall rule to allow VPC Connector to access CRM service
resource "google_compute_firewall" "allow_connector_to_crm" {
  name    = "allow-accounting-connector-to-crm"
  network = data.google_compute_network.crm_vpc.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  # VPC Connector uses IPs from this range
  source_ranges = ["10.3.1.0/28"]
  target_tags   = ["crm-server"]
  
  description = "Allow VPC Connector (accounting service) to access CRM service"

  depends_on = [google_project_service.accounting_apis]
}

# Define the Cloud Run service
resource "google_cloud_run_v2_service" "accounting_api_service" {
  name     = "accounting-api-service"
  location = "us-central1"
  project  = var.project_id

  template {
    containers {
      # Note: You need to build and push the image first using:
      # cd multicloud/gcp/accounting-service && gcloud builds submit --config=cloudbuild.yaml
      image = "us-central1-docker.pkg.dev/${var.project_id}/accounting-repo/accounting-service:latest"
      
      ports {
        container_port = 8080
      }

      # Environment variables
      env {
        name  = "CRM_SERVICE_URL"
        value = var.crm_service_url
      }

      # Resource limits
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    # Scaling configuration
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    # VPC Connector configuration for accessing CRM service
    vpc_access {
      # Use VPC Connector (legacy approach, different from Direct VPC egress)
      connector = google_vpc_access_connector.accounting_connector.id
      # Route only private ranges through VPC (more efficient)
      egress = "PRIVATE_RANGES_ONLY"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.accounting_apis,
    google_artifact_registry_repository.accounting_repo,
    google_vpc_access_connector.accounting_connector
  ]
}

# Allow unauthenticated access to the Cloud Run service
resource "google_cloud_run_v2_service_iam_member" "accounting_noauth" {
  name     = google_cloud_run_v2_service.accounting_api_service.name
  location = google_cloud_run_v2_service.accounting_api_service.location
  project  = google_cloud_run_v2_service.accounting_api_service.project
  role     = "roles/run.invoker"
  member   = "allUsers"
  
  depends_on = [google_cloud_run_v2_service.accounting_api_service]
}

# Output the URL of the deployed service
output "accounting_service_url" {
  description = "The URL of the deployed Cloud Run accounting service"
  value       = google_cloud_run_v2_service.accounting_api_service.uri
}

output "accounting_artifact_registry" {
  description = "The Artifact Registry repository for accounting service"
  value       = google_artifact_registry_repository.accounting_repo.id
}

output "accounting_vpc_connector" {
  description = "VPC Connector configuration for accounting service"
  value = {
    name       = google_vpc_access_connector.accounting_connector.name
    ip_range   = google_vpc_access_connector.accounting_connector.ip_cidr_range
    network    = data.google_compute_network.crm_vpc.name
    throughput = "${google_vpc_access_connector.accounting_connector.min_throughput}-${google_vpc_access_connector.accounting_connector.max_throughput} Mbps"
  }
}

