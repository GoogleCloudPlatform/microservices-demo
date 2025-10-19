# Enable necessary APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com"
  ])
  project            = "network-obs-demo"
  service            = each.key
  disable_on_destroy = false
}

# Define the Cloud Run service with hardcoded values
resource "google_cloud_run_v2_service" "food_api_service" {
  name     = "food-api-service"
  location = "europe-west1"
  project  = "network-obs-demo"

  template {
    containers {
      image = "europe-west1-docker.pkg.dev/network-obs-demo/food-repo/food-service:latest"
      ports {
        container_port = 8080
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.apis]
}

# Allow unauthenticated access to the Cloud Run service
resource "google_cloud_run_v2_service_iam_member" "noauth" {
  name     = google_cloud_run_v2_service.food_api_service.name
  location = google_cloud_run_v2_service.food_api_service.location
  project  = google_cloud_run_v2_service.food_api_service.project
  role     = "roles/run.invoker"
  member   = "allUsers"
  depends_on = [google_cloud_run_v2_service.food_api_service]
}

# Output the URL of the deployed service
output "service_url" {
  description = "The URL of the deployed Cloud Run service."
  value       = google_cloud_run_v2_service.food_api_service.uri
}

