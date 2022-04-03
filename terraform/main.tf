provider "google" {
	project = "co-libry-services"
	region = "europe-west1"
	zone = "europe-west1-b"
}

data "google_client_config" "default" {}

provider "kubernetes" {
  alias                  = "gke-cluster-west"
  host                   = "https://${module.gke-cluster-europe-west1.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke-cluster-europe-west1.ca_certificate)
}

provider "kubernetes" {
  alias                  = "gke-cluster-north"
  host                   = "https://${module.gke-cluster-europe-north1.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke-cluster-europe-north1.ca_certificate)
}

# Network module for cluster in europe west
# Exists of main network and one subnet with two secondary ip ranges.
module "boutique-west-network" {
  source       = "terraform-google-modules/network/google"
  project_id   = "co-libry-services"
  network_name = "boutique-west"
  version      = "~> 4.0"

  subnets = [
    {
      subnet_name           = "gke-cluster-europe-west1-01"
      subnet_ip             = "10.0.0.0/16"
      subnet_region         = "europe-west1"
      subnet_private_access = "false"
      subnet_flow_logs      = "true"
    }
  ]

  secondary_ranges = {
    "gke-cluster-europe-west1-01" = [   
      {
        ip_cidr_range = "10.1.0.0/16"
        range_name = "pods-west-01"
      },
      {
        ip_cidr_range = "10.2.0.0/16",
        range_name = "services-west-01"
      } 
    ]
  }
}

module "boutique-north-network" {
  source       = "terraform-google-modules/network/google"
  project_id   = "co-libry-services"
  network_name = "boutique-north"
  version      = "~> 4.0"

  subnets = [
    {
      subnet_name           = "gke-cluster-europe-north1-01"
      subnet_ip             = "10.0.0.0/16"
      subnet_region         = "europe-north1"
      subnet_private_access = "false"
      subnet_flow_logs      = "true"
    }
  ]

  secondary_ranges = {
    "gke-cluster-europe-north1-01" = [ 
      {
        ip_cidr_range = "10.1.0.0/16"
        range_name    = "pods-north-01"
      },
      {
        ip_cidr_range = "10.2.0.0/16",
        range_name    = "services-north-01"
      } 
    ]
  }
}

module "gke-cluster-europe-west1" {
  source     = "terraform-google-modules/kubernetes-engine/google"
  project_id = "co-libry-services"
  name       = "cluster-europe-west1"
  regional   = false
  zones      = ["europe-west1-b"]

  network                = module.boutique-west-network.network_name
  subnetwork             = module.boutique-west-network.subnets_names[0]
  ip_range_pods          = "pods-west-01"
  ip_range_services      = "services-west-01"
  create_service_account = true

  node_pools = [
    {
      name               = "node-pool-west1"
      machine_type       = "e2-standard-2"
      min_count          = 1
      max_count          = 4
      disk_size_gb       = 100
      disk_type          = "pd-ssd"
      image_type         = "COS"
      auto_repair        = true
      auto_upgrade       = false
      preemptible        = false
      initial_node_count = 1
    },
  ]

  node_pools_labels = {
    all = {}

    node-pool-west1 = {
      default-node-pool = true
    }
  }

  node_pools_oauth_scopes = {
    all = []

    node-pool-wes1 = [
      "https://www.googleapis.com/auth/trace.append",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/servicecontrol",
    ]
  }
}

module "gke-cluster-europe-north1" {
  source     = "terraform-google-modules/kubernetes-engine/google"
  project_id = "co-libry-services"
  name       = "cluster-europe-north1"
  regional   = false
  zones      = ["europe-north1-b"]

  network                 = module.boutique-north-network.network_name
  subnetwork              = module.boutique-north-network.subnets_names[0]
  ip_range_pods           = "pods-north-01"
  ip_range_services       = "services-north-01"
  create_service_account  = true
  remove_default_node_pool = true
  initial_node_count       = 1

  node_pools = [
    {
      name               = "node-pool-north1"
      machine_type       = "n1-standard-1"
      min_count          = 1
      max_count          = 4
      disk_size_gb       = 100
      disk_type          = "pd-ssd"
      image_type         = "COS"
      auto_repair        = true
      auto_upgrade       = false
      preemptible        = false
      initial_node_count = 1
    },
  ]

  node_pools_labels = {
    all = {}

    node-pool-north1 = {
      default-node-pool = true
    }
  }


  node_pools_oauth_scopes = {
    all = []

    node-pool-north1 = [
      "https://www.googleapis.com/auth/trace.append",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/servicecontrol",
    ]
  }
}
