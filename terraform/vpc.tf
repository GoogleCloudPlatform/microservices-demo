provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC
resource "google_compute_network" "vpc" {
  name                    = "${var.app_name}-vpc"
  auto_create_subnetworks = "false"
}

# Subnets
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.app_name}-subnet"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = var.gke_nodes_cidr
  secondary_ip_range {
    range_name    = "services-range"
    ip_cidr_range = var.gke_services_cidr
  }
  secondary_ip_range {
    range_name    = "pods-range"
    ip_cidr_range = var.gke_pods_cidr
  }
}
