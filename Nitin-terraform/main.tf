provider "google" {
  project = "gke-demo-448110"
  region  = "asia-south1-a"
}

resource "google_container_cluster" "primary" {
  name     = "microservices-cluster"
  location = var.region
  initial_node_count = 4

  node_config {
    machine_type = "e2-medium"
  }
}

