# crm.tf - GCP CRM Service Infrastructure
# Note: Uses shared terraform, variable, and provider configurations from main.tf

# 1. Create a dedicated VPC network for the CRM service
resource "google_compute_network" "crm_vpc" {
  name                    = "crm-vpc"
  auto_create_subnetworks = false
  description             = "Dedicated VPC for CRM service"
}

# 2. Create a subnet in the CRM VPC
resource "google_compute_subnetwork" "crm_subnet" {
  name          = "crm-subnet"
  ip_cidr_range = "10.3.0.0/24"
  region        = "asia-east1"
  network       = google_compute_network.crm_vpc.id
  description   = "Subnet for CRM service"
}

# 2a. Create static internal IP addresses for VMs
resource "google_compute_address" "crm_backend_static_ip" {
  name         = "crm-backend-static-ip"
  address_type = "INTERNAL"
  address      = "10.3.0.2"
  region       = "asia-east1"
  subnetwork   = google_compute_subnetwork.crm_subnet.id
  description  = "Static internal IP for CRM backend VM"
}

resource "google_compute_address" "crm_frontend_static_ip" {
  name         = "crm-frontend-static-ip"
  address_type = "INTERNAL"
  address      = "10.3.0.3"
  region       = "asia-east1"
  subnetwork   = google_compute_subnetwork.crm_subnet.id
  description  = "Static internal IP for CRM frontend VM"
}

resource "google_compute_address" "crm_status_static_ip" {
  name         = "crm-status-static-ip"
  address_type = "INTERNAL"
  address      = "10.3.0.4"
  region       = "asia-east1"
  subnetwork   = google_compute_subnetwork.crm_subnet.id
  description  = "Static internal IP for CRM status VM"
}

# 2b. Create static external IP for status VM
resource "google_compute_address" "crm_status_external_ip" {
  name        = "crm-status-external-ip"
  region      = "asia-east1"
  description = "Static external IP for CRM status VM (public access)"
}

# ============================================================================
# CLOUD STORAGE BUCKET WITH PRIVATE SERVICE CONNECT
# ============================================================================

# 2c. Enable Cloud Storage API
resource "google_project_service" "storage_api" {
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}

# 2d. Create Cloud Storage bucket for CRM API logs
resource "google_storage_bucket" "crm_logs_bucket" {
  name          = "crm-online-boutique-bucket"
  location      = "US-CENTRAL1"
  storage_class = "STANDARD"
  project       = var.project_id
  
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  depends_on = [google_project_service.storage_api]
}

# Note: PSC endpoint for Cloud Storage is not required.
# GCP VMs can access Cloud Storage directly through service account authentication
# without needing a Private Service Connect endpoint. The storage client library
# automatically uses Google's private network paths when running on GCP.

# 2g. Service account for CRM backend
resource "google_service_account" "crm_backend_sa" {
  account_id   = "crm-backend-sa"
  display_name = "CRM Backend Service Account"
  project      = var.project_id
  description  = "Service account for CRM backend VM with GCS access"
}

# 2h. Grant storage object creator role
resource "google_storage_bucket_iam_member" "crm_backend_bucket_access" {
  bucket = google_storage_bucket.crm_logs_bucket.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.crm_backend_sa.email}"
}

# 2d. Create Cloud Router for NAT
resource "google_compute_router" "crm_router" {
  name    = "crm-router"
  region  = "asia-east1"
  network = google_compute_network.crm_vpc.id

  bgp {
    asn = 64514
  }
}

# 2e. Create Cloud NAT for internet access
resource "google_compute_router_nat" "crm_nat" {
  name                               = "crm-nat"
  router                             = google_compute_router.crm_router.name
  region                             = "asia-east1"
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# 3. Create a firewall rule to allow traffic on port 8080 from online-boutique-vpc VPC
resource "google_compute_firewall" "allow_crm_http" {
  name    = "crm-allow-http-internal"
  network = google_compute_network.crm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  target_tags   = ["crm-server"]
  source_ranges = ["10.128.0.0/9", "10.3.0.0/24"] # Online-boutique-vpc VPC and CRM VPC ranges
}

# 4. Create CRM Backend VM instance with static IP
resource "google_compute_instance" "crm_vm" {
  name         = "crm-backend-vm"
  machine_type = "e2-small"
  zone         = "asia-east1-a"

  tags = ["crm-server"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.crm_vpc.id
    subnetwork = google_compute_subnetwork.crm_subnet.id
    network_ip = google_compute_address.crm_backend_static_ip.address
    // No access_config block = no external IP (private only)
  }

  # Service account for GCS access
  service_account {
    email  = google_service_account.crm_backend_sa.email
    scopes = ["cloud-platform"]
  }

  # Startup script from external file
  metadata_startup_script = file("${path.module}/crm-backend/startup.sh")
}

# Output the private IP address for internal communication
output "crm_service_url" {
  value       = "http://${google_compute_address.crm_backend_static_ip.address}:8080/customers"
  description = "The URL to access the CRM service via private IP."
}

output "crm_vm_private_ip" {
  value       = google_compute_address.crm_backend_static_ip.address
  description = "The private IP address of the CRM VM."
}

output "crm_vpc_name" {
  value       = google_compute_network.crm_vpc.name
  description = "The name of the CRM VPC network."
}

output "crm_subnet_cidr" {
  value       = google_compute_subnetwork.crm_subnet.ip_cidr_range
  description = "The CIDR range of the CRM subnet."
}

# ============================================================================
# OLD EMBEDDED SCRIPT REMOVED - NOW USING EXTERNAL FILE
# The original embedded startup script (lines 80-161) has been moved to:
# crm-backend/startup.sh
# ============================================================================

# 5. Create VPC peering from crm-vpc to online-boutique-vpc VPC
resource "google_compute_network_peering" "crm_to_ob" {
  name         = "crm-to-ob-peering"
  network      = google_compute_network.crm_vpc.id
  peer_network = "projects/${var.project_id}/global/networks/online-boutique-vpc"

  import_custom_routes = false
  export_custom_routes = false
}

# 6. Create VPC peering from online-boutique-vpc VPC to crm-vpc  
resource "google_compute_network_peering" "ob_to_crm" {
  name         = "ob-to-crm-peering"
  network      = "projects/${var.project_id}/global/networks/online-boutique-vpc"
  peer_network = google_compute_network.crm_vpc.id

  import_custom_routes = false
  export_custom_routes = false
}

# 7. Create VPC peering from remote VPC to online-boutique-vpc 
# Note: This peering is managed by the remote project owner (cci-dev-playground)
# and cannot be managed from this Terraform configuration
# resource "google_compute_network_peering" "remote_to_ob" {
#   name         = "remote-to-ob-peering"
#   network      = "projects/${var.peering_project_id}/global/networks/${var.peering_vpc_network}"
#   peer_network = "projects/${var.project_id}/global/networks/online-boutique-vpc"
#
#   import_custom_routes = false
#   export_custom_routes = true
# }

# 8. Create VPC peering from online-boutique-vpc VPC to remote  
resource "google_compute_network_peering" "ob_to_remote" {
  name         = "ob-to-remote-peering"
  network      = "projects/${var.project_id}/global/networks/online-boutique-vpc"
  peer_network = "projects/${var.peering_project_id}/global/networks/${var.peering_vpc_network}"

  import_custom_routes = true
  export_custom_routes = false
}

# ============================================================================
# CRM FRONTEND - Customer Dashboard with L7 Load Balancer
# ============================================================================

# 9. Create CRM Frontend VM instance with static IP
resource "google_compute_instance" "crm_frontend_vm" {
  name         = "crm-frontend-vm"
  machine_type = "e2-micro"
  zone         = "asia-east1-a"

  tags = ["crm-frontend", "http-server"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.crm_vpc.id
    subnetwork = google_compute_subnetwork.crm_subnet.id
    network_ip = google_compute_address.crm_frontend_static_ip.address
    // No external IP - accessed via Load Balancer
  }

  # Startup script from external file
  metadata_startup_script = file("${path.module}/crm-frontend/startup.sh")
}

# ============================================================================
# OLD EMBEDDED SCRIPT REMOVED - NOW USING EXTERNAL FILE
# The original embedded startup script (lines 252-445) has been moved to:
# crm-frontend/startup.sh
# ============================================================================

# 10. Create instance group for the frontend VM
resource "google_compute_instance_group" "crm_frontend_group" {
  name        = "crm-frontend-instance-group"
  description = "Instance group for CRM frontend"
  zone        = "asia-east1-a"

  instances = [
    google_compute_instance.crm_frontend_vm.id
  ]

  named_port {
    name = "http8080"
    port = "8080"
  }
}

# 11. Create health check for frontend
resource "google_compute_health_check" "crm_frontend_health" {
  name                = "crm-frontend-health-check"
  check_interval_sec  = 10
  timeout_sec         = 5
  healthy_threshold   = 2
  unhealthy_threshold = 3

  http_health_check {
    port         = 8080
    request_path = "/health"
  }
}

# 12. Create backend service (using EXTERNAL_MANAGED for better configuration)
resource "google_compute_backend_service" "crm_frontend_backend" {
  name                  = "crm-frontend-backend"
  protocol              = "HTTP"
  port_name             = "http8080"
  timeout_sec           = 30
  health_checks         = [google_compute_health_check.crm_frontend_health.id]
  load_balancing_scheme = "EXTERNAL_MANAGED"

  backend {
    group           = google_compute_instance_group.crm_frontend_group.id
    balancing_mode  = "UTILIZATION"
    capacity_scaler = 1.0
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }
}

# 13. Create URL map
resource "google_compute_url_map" "crm_frontend_url_map" {
  name            = "crm-frontend-url-map"
  default_service = google_compute_backend_service.crm_frontend_backend.id
}

# 14. Create target HTTP proxy
resource "google_compute_target_http_proxy" "crm_frontend_proxy" {
  name    = "crm-frontend-http-proxy"
  url_map = google_compute_url_map.crm_frontend_url_map.id
}

# 15. Reserve a static external IP for the load balancer
resource "google_compute_global_address" "crm_frontend_ip" {
  name = "crm-frontend-lb-ip"
}

# 16. Create global forwarding rule (this is the external IP that users access)
resource "google_compute_global_forwarding_rule" "crm_frontend_forwarding_rule" {
  name                  = "crm-frontend-forwarding-rule"
  target                = google_compute_target_http_proxy.crm_frontend_proxy.id
  port_range            = "80"
  ip_address            = google_compute_global_address.crm_frontend_ip.address
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# 17. Firewall rule to allow health checks from Google Cloud load balancers
resource "google_compute_firewall" "crm_frontend_health_check" {
  name    = "crm-frontend-allow-health-check"
  network = google_compute_network.crm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  # Google Cloud health check IP ranges
  source_ranges = ["35.191.0.0/16", "130.211.0.0/22"]
  target_tags   = ["crm-frontend"]
}

# 18. Firewall rule to allow HTTP traffic from load balancer to frontend instances
resource "google_compute_firewall" "crm_frontend_allow_lb" {
  name    = "crm-frontend-allow-lb"
  network = google_compute_network.crm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  # Google Cloud load balancer IP ranges
  source_ranges = ["35.191.0.0/16", "130.211.0.0/22"]
  target_tags   = ["crm-frontend"]
}

# 19. Firewall rule to allow frontend to communicate with backend
resource "google_compute_firewall" "crm_frontend_to_backend" {
  name    = "crm-frontend-to-backend"
  network = google_compute_network.crm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_tags = ["crm-frontend"]
  target_tags = ["crm-server"]
}

# Outputs for frontend
output "crm_frontend_url" {
  value       = "http://${google_compute_global_address.crm_frontend_ip.address}"
  description = "Public URL to access the CRM frontend dashboard"
}

output "crm_frontend_ip" {
  value       = google_compute_global_address.crm_frontend_ip.address
  description = "Static external IP address of the CRM frontend load balancer"
}

output "crm_frontend_vm_private_ip" {
  value       = google_compute_address.crm_frontend_static_ip.address
  description = "Private IP address of the CRM frontend VM"
}

# ============================================================================
# CRM STATUS MONITOR - Public VM for Direct Internet Access Demo
# ============================================================================

# 20. Create CRM Status VM instance with static IPs (internal and external)
resource "google_compute_instance" "crm_status_vm" {
  name         = "crm-public-status-vm"
  machine_type = "e2-micro"
  zone         = "asia-east1-a"

  tags = ["crm-status", "http-server"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.crm_vpc.id
    subnetwork = google_compute_subnetwork.crm_subnet.id
    network_ip = google_compute_address.crm_status_static_ip.address

    # External IP for direct internet access
    access_config {
      nat_ip = google_compute_address.crm_status_external_ip.address
    }
  }

  # Startup script from external file
  metadata_startup_script = file("${path.module}/crm-status/startup.sh")
}

# 21. Firewall rule to allow HTTP traffic from internet to status VM
resource "google_compute_firewall" "crm_status_allow_http" {
  name    = "crm-status-allow-http-internet"
  network = google_compute_network.crm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  # Allow from anywhere on the internet
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["crm-status"]
}

# 22. Firewall rule to allow status VM to communicate with backend
resource "google_compute_firewall" "crm_status_to_backend" {
  name    = "crm-status-to-backend"
  network = google_compute_network.crm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_tags = ["crm-status"]
  target_tags = ["crm-server"]
}

# Outputs for status VM
output "crm_status_public_ip" {
  value       = google_compute_address.crm_status_external_ip.address
  description = "Static external IP address of the CRM status VM"
}

output "crm_status_url" {
  value       = "http://${google_compute_address.crm_status_external_ip.address}"
  description = "Public URL to access the CRM status monitor (direct VM access)"
}

output "crm_status_vm_private_ip" {
  value       = google_compute_address.crm_status_static_ip.address
  description = "Private IP address of the CRM status VM"
}

output "crm_storage_bucket" {
  value       = google_storage_bucket.crm_logs_bucket.name
  description = "Cloud Storage bucket for CRM API logs"
}

# ============================================================================
# END OF CRM INFRASTRUCTURE
# This file has been refactored to use external startup scripts:
# - crm-backend/startup.sh (CRM backend service)
# - crm-frontend/startup.sh (CRM frontend dashboard)
# - crm-status/startup.sh (CRM status monitor)
# All VMs now use static IP addresses for stability.
# ============================================================================
