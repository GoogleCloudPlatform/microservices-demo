provider "google" {
  project = var.project
  region  = var.region
}

terraform {
  backend "gcs" {
    bucket  = "microservices-bucket-tfstate"
    prefix  = "terraform/state"
  }
}

# VPC and Subnets
resource "google_compute_network" "my_vpc" {
  name                    = var.network_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "dev_subnet" {
  name          = var.dev_subnet_name
  ip_cidr_range = cidrsubnet(var.subnet_cidr, 4, 0)
  network       = google_compute_network.my_vpc.self_link
  region        = var.region
}

resource "google_compute_subnetwork" "prod_subnet" {
  name          = var.prod_subnet_name
  ip_cidr_range = cidrsubnet(var.subnet_cidr, 4, 1)
  network       = google_compute_network.my_vpc.self_link
  region        = var.region
}

# GKE Cluster
resource "google_container_cluster" "my_gke_cluster" {
  name     = var.gke_cluster_name
  location = var.region
   remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "my-node-pool"
  location   = "us-east4"
  cluster    = google_container_cluster.my_gke_cluster.id
  node_count = 1

  node_config {
    preemptible  = true
    machine_type = "e2-custom-8-10240"

    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    service_account = "token-microservices@alien-segment-410723.iam.gserviceaccount.com"
    oauth_scopes    = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
resource "google_artifact_registry_repository" "microservices-demo-final" {
  location      = "us-east4"
  repository_id = "microservices-demo-final"
  description   = "docker repository for my GKE"
  format        = "DOCKER"
}


#Pipelinetest 2
