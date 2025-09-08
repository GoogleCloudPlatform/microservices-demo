resource "google_compute_network" "furniture_vpc" {
  name                    = "furniture-vpc"
  auto_create_subnetworks = false
  project                 = var.gcp_project_id
  routing_mode            = "GLOBAL"
}

resource "google_compute_subnetwork" "furniture_subnet" {
  name          = "furniture-subnet-us-central1"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.furniture_vpc.id
  project       = var.gcp_project_id
}

# Firewall rule to allow SSH access
resource "google_compute_firewall" "furniture_vpc_allow_ssh" {
  name    = "furniture-vpc-allow-ssh"
  network = google_compute_network.furniture_vpc.name
  project = var.gcp_project_id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = ["0.0.0.0/0"] # Be more restrictive in production
}

# Firewall rule to allow application traffic on port 3000
resource "google_compute_firewall" "furniture_vpc_allow_app" {
  name    = "furniture-vpc-allow-app"
  network = google_compute_network.furniture_vpc.name
  project = var.gcp_project_id

  allow {
    protocol = "tcp"
    ports    = ["3000"]
  }
  # Allow from anywhere for testing, including the peer VPC ranges
  source_ranges = ["0.0.0.0/0"]
}

# Create the Compute Engine VM
resource "google_compute_instance" "furniture_vm" {
  name         = "furniture-vm"
  machine_type = "e2-small"
  zone         = var.zone
  project      = var.gcp_project_id

  tags = ["furniture-app"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12" # Using Debian 12
    }
  }

  network_interface {
    network    = google_compute_network.furniture_vpc.id
    subnetwork = google_compute_subnetwork.furniture_subnet.id
  }

  metadata_startup_script = file("${path.module}/furniture_startup.sh")
}

output "instance_internal_ip" {
  description = "Internal IP address of the furniture VM"
  value       = google_compute_instance.furniture_vm.network_interface[0].network_ip
}

data "google_compute_network" "ob_network" {
  name    = var.ob_network_name
  project = var.gcp_project_id
}

data "google_compute_subnetwork" "ob_subnet" {
  name    = var.ob_subnet_name
  region  = var.region
  project = var.gcp_project_id
}

# -----------------------------------------------------------------------------
# HA VPN Configuration
# -----------------------------------------------------------------------------

# Shared secret for VPN tunnels
resource "random_id" "vpn_shared_secret" {
  byte_length = 16
}

# --- Resources for furniture-vpc ---
resource "google_compute_ha_vpn_gateway" "furniture_ha_gateway" {
  name    = "furniture-ha-gateway"
  region  = var.region
  network = google_compute_network.furniture_vpc.id
  project = var.gcp_project_id
}

resource "google_compute_router" "furniture_router" {
  name    = "furniture-router"
  region  = var.region
  network = google_compute_network.furniture_vpc.name
  project = var.gcp_project_id
  bgp {
    asn = 65001
  }
}

# --- Resources for online-boutique-vpc ---
resource "google_compute_ha_vpn_gateway" "boutique_ha_gateway" {
  name    = "boutique-ha-gateway"
  region  = var.region
  network = data.google_compute_network.ob_network.id
  project = var.gcp_project_id
}

resource "google_compute_router" "boutique_router" {
  name    = "boutique-router"
  region  = var.region
  network = data.google_compute_network.ob_network.name
  project = var.gcp_project_id
  bgp {
    asn = 65002
    # Advertise the subnet and the GKE pod range
    advertise_mode = "CUSTOM"
    advertised_ip_ranges {
      range       = data.google_compute_subnetwork.ob_subnet.ip_cidr_range
      description = "Boutique Subnet"
    }
    advertised_ip_ranges {
      range       = var.ob_gke_pod_range[0]
      description = "Boutique GKE Pods"
    }
    # Add GKE Service range here if needed
  }
}

# --- VPN Tunnels ---
# Tunnel 1: furniture-gateway Interface 0 to boutique-gateway Interface 0
resource "google_compute_vpn_tunnel" "tunnel_a_to_b_if0" {
  name                          = "tunnel-furniture-to-boutique-if0"
  region                        = var.region
  project                       = var.gcp_project_id
  peer_gcp_gateway              = google_compute_ha_vpn_gateway.boutique_ha_gateway.id
  shared_secret                 = random_id.vpn_shared_secret.hex
  router                        = google_compute_router.furniture_router.id
  vpn_gateway                   = google_compute_ha_vpn_gateway.furniture_ha_gateway.id
  vpn_gateway_interface         = 0
  ike_version                   = 2
  local_traffic_selector        = ["0.0.0.0/0"]
  remote_traffic_selector       = ["0.0.0.0/0"]
}

# Tunnel 2: furniture-gateway Interface 1 to boutique-gateway Interface 1
resource "google_compute_vpn_tunnel" "tunnel_a_to_b_if1" {
  name                          = "tunnel-furniture-to-boutique-if1"
  region                        = var.region
  project                       = var.gcp_project_id
  peer_gcp_gateway              = google_compute_ha_vpn_gateway.boutique_ha_gateway.id
  shared_secret                 = random_id.vpn_shared_secret.hex
  router                        = google_compute_router.furniture_router.id
  vpn_gateway                   = google_compute_ha_vpn_gateway.furniture_ha_gateway.id
  vpn_gateway_interface         = 1
  ike_version                   = 2
  local_traffic_selector        = ["0.0.0.0/0"]
  remote_traffic_selector       = ["0.0.0.0/0"]
}

# --- BGP Sessions on furniture-router ---
resource "google_compute_router_interface" "furniture_if0" {
  name       = "if0-tunnel-a-b-if0"
  router     = google_compute_router.furniture_router.name
  region     = var.region
  project    = var.gcp_project_id
  ip_range   = "169.254.0.1/30"
  vpn_tunnel = google_compute_vpn_tunnel.tunnel_a_to_b_if0.name
}

resource "google_compute_router_peer" "furniture_peer0" {
  name                      = "peer0-boutique"
  router                    = google_compute_router.furniture_router.name
  region                    = var.region
  project                   = var.gcp_project_id
  peer_ip_address           = "169.254.0.2"
  peer_asn                  = google_compute_router.boutique_router.bgp[0].asn
  interface                 = google_compute_router_interface.furniture_if0.name
  ike_version               = 2
  enable_ipv6               = false
}

resource "google_compute_router_interface" "furniture_if1" {
  name       = "if1-tunnel-a-b-if1"
  router     = google_compute_router.furniture_router.name
  region     = var.region
  project    = var.gcp_project_id
  ip_range   = "169.254.1.1/30"
  vpn_tunnel = google_compute_vpn_tunnel.tunnel_a_to_b_if1.name
}

resource "google_compute_router_peer" "furniture_peer1" {
  name                      = "peer1-boutique"
  router                    = google_compute_router.furniture_router.name
  region                    = var.region
  project                   = var.gcp_project_id
  peer_ip_address           = "169.254.1.2"
  peer_asn                  = google_compute_router.boutique_router.bgp[0].asn
  interface                 = google_compute_router_interface.furniture_if1.name
  ike_version               = 2
  enable_ipv6               = false
}

# --- BGP Sessions on boutique-router ---
resource "google_compute_router_interface" "boutique_if0" {
  name       = "if0-tunnel-a-b-if0"
  router     = google_compute_router.boutique_router.name
  region     = var.region
  project    = var.gcp_project_id
  ip_range   = "169.254.0.2/30"
  vpn_tunnel = google_compute_vpn_tunnel.tunnel_a_to_b_if0.name
}

resource "google_compute_router_peer" "boutique_peer0" {
  name                      = "peer0-furniture"
  router                    = google_compute_router.boutique_router.name
  region                    = var.region
  project                   = var.gcp_project_id
  peer_ip_address           = "169.254.0.1"
  peer_asn                  = google_compute_router.furniture_router.bgp[0].asn
  interface                 = google_compute_router_interface.boutique_if0.name
  ike_version               = 2
  enable_ipv6               = false
  # Advertisement handled at the router level for boutique-router
}

resource "google_compute_router_interface" "boutique_if1" {
  name       = "if1-tunnel-a-b-if1"
  router     = google_compute_router.boutique_router.name
  region     = var.region
  project    = var.gcp_project_id
  ip_range   = "169.254.1.2/30"
  vpn_tunnel = google_compute_vpn_tunnel.tunnel_a_to_b_if1.name
}

resource "google_compute_router_peer" "boutique_peer1" {
  name                      = "peer1-furniture"
  router                    = google_compute_router.boutique_router.name
  region                    = var.region
  project                   = var.gcp_project_id
  peer_ip_address           = "169.254.1.1"
  peer_asn                  = google_compute_router.furniture_router.bgp[0].asn
  interface                 = google_compute_router_interface.boutique_if1.name
  ike_version               = 2
  enable_ipv6               = false
  # Advertisement handled at the router level for boutique-router
}