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

  # This startup script runs automatically when the VM is created
  metadata_startup_script = <<-EOT
    #!/bin/bash
    
    # Update packages and install Node.js and npm
    sudo apt-get update
    sudo apt-get install -y nodejs npm

    # Install pm2, a production process manager for Node.js
    sudo npm install pm2 -g

    # Create a directory for the app
    sudo mkdir -p /opt/app
    sudo chown -R $(whoami):$(whoami) /opt/app
    cd /opt/app

    # Create the package.json file
    cat <<'EOF' > package.json
    {
      "name": "mock-furniture-service",
      "version": "1.0.0",
      "main": "app.js",
      "dependencies": {
        "express": "^4.18.2"
      }
    }
    EOF

    # Create the app.js file with the mock furniture logic
    cat <<'EOF' > app.js
    const express = require('express');
    const app = express();
    const port = 8080;

    // Middleware to parse JSON bodies
    app.use(express.json());

    // In-memory data store with two hardcoded items
    let items = [
      { name: 'chair', brand: 'ikea' },
      { name: 'table', surname: 'jysk' }
    ];

    // GET endpoint to list all items
    app.get('/furniture', (req, res) => {
      console.log('GET /furniture - Returning items list');
      res.status(200).json(items);
    });

    // POST endpoint to add a new item
    app.post('/furniture', (req, res) => {
      const { name, brand } = req.body;

      if (!name || !brand) {
        console.log('POST /furniture - Failed: Missing name or brand');
        return res.status(400).json({ error: 'Name and brand are required.' });
      }

      const newItem = { name, brand };
      items.push(newItem);
      
      // Cleanup: Keep only the 10 most recent items
      if (items.length > 10) {
        const removedCount = items.length - 10;
        items = items.slice(-10); // Keep last 10
        console.log(`POST /furniture - Cleaned up $${removedCount} old items(s), keeping 10 most recent`);
      }
      
      console.log(`POST /furniture - Added new iten: $${name} $${brand}. Total: $${items.length}`);
      res.status(201).json(newItem);
    });

    app.listen(port, '0.0.0.0', () => {
      console.log(`Mock furniture server listening on port $${port}`);
    });
    EOF

    # Install application dependencies
    npm install

    # Start the application using pm2 to run it in the background
    pm2 start app.js --name "crm-app"
  EOT
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
resource "google_compute_ha_vpn_gateway" "ha_gateway1" {
  region  = "us-central1"
  name    = "ha-vpn-1"
  network = google_compute_network.ob_network.id
}

resource "google_compute_ha_vpn_gateway" "ha_gateway2" {
  region  = "us-central1"
  name    = "ha-vpn-2"
  network = google_compute_network.furniture_vpc.id
}

resource "google_compute_router" "router1" {
  name    = "ha-vpn-router1"
  region  = "us-central1"
  network = google_compute_network.ob_network.name
  bgp {
    asn = 64514
  }
}

resource "google_compute_router" "router2" {
  name    = "ha-vpn-router2"
  region  = "us-central1"
  network = google_compute_network.furniture_vpc.name
  bgp {
    asn = 64515
  }
}

resource "google_compute_vpn_tunnel" "tunnel1" {
  name                  = "ha-vpn-tunnel1"
  region                = "us-central1"
  vpn_gateway           = google_compute_ha_vpn_gateway.ha_gateway1.id
  peer_gcp_gateway      = google_compute_ha_vpn_gateway.ha_gateway2.id
  shared_secret         = "a secret message"
  router                = google_compute_router.router1.id
  vpn_gateway_interface = 0
}

resource "google_compute_vpn_tunnel" "tunnel2" {
  name                  = "ha-vpn-tunnel2"
  region                = "us-central1"
  vpn_gateway           = google_compute_ha_vpn_gateway.ha_gateway1.id
  peer_gcp_gateway      = google_compute_ha_vpn_gateway.ha_gateway2.id
  shared_secret         = "a secret message"
  router                = google_compute_router.router1.id
  vpn_gateway_interface = 1
}

resource "google_compute_vpn_tunnel" "tunnel3" {
  name                  = "ha-vpn-tunnel3"
  region                = "us-central1"
  vpn_gateway           = google_compute_ha_vpn_gateway.ha_gateway2.id
  peer_gcp_gateway      = google_compute_ha_vpn_gateway.ha_gateway1.id
  shared_secret         = "a secret message"
  router                = google_compute_router.router2.id
  vpn_gateway_interface = 0
}

resource "google_compute_vpn_tunnel" "tunnel4" {
  name                  = "ha-vpn-tunnel4"
  region                = "us-central1"
  vpn_gateway           = google_compute_ha_vpn_gateway.ha_gateway2.id
  peer_gcp_gateway      = google_compute_ha_vpn_gateway.ha_gateway1.id
  shared_secret         = "a secret message"
  router                = google_compute_router.router2.id
  vpn_gateway_interface = 1
}

resource "google_compute_router_interface" "router1_interface1" {
  name       = "router1-interface1"
  router     = google_compute_router.router1.name
  region     = "us-central1"
  ip_range   = "169.254.0.1/30"
  vpn_tunnel = google_compute_vpn_tunnel.tunnel1.name
}

resource "google_compute_router_peer" "router1_peer1" {
  name                      = "router1-peer1"
  router                    = google_compute_router.router1.name
  region                    = "us-central1"
  peer_ip_address           = "169.254.0.2"
  peer_asn                  = 64515
  advertised_route_priority = 100
  interface                 = google_compute_router_interface.router1_interface1.name
}

resource "google_compute_router_interface" "router1_interface2" {
  name       = "router1-interface2"
  router     = google_compute_router.router1.name
  region     = "us-central1"
  ip_range   = "169.254.1.2/30"
  vpn_tunnel = google_compute_vpn_tunnel.tunnel2.name
}

resource "google_compute_router_peer" "router1_peer2" {
  name                      = "router1-peer2"
  router                    = google_compute_router.router1.name
  region                    = "us-central1"
  peer_ip_address           = "169.254.1.1"
  peer_asn                  = 64515
  advertised_route_priority = 100
  interface                 = google_compute_router_interface.router1_interface2.name
}

resource "google_compute_router_interface" "router2_interface1" {
  name       = "router2-interface1"
  router     = google_compute_router.router2.name
  region     = "us-central1"
  ip_range   = "169.254.0.2/30"
  vpn_tunnel = google_compute_vpn_tunnel.tunnel3.name
}

resource "google_compute_router_peer" "router2_peer1" {
  name                      = "router2-peer1"
  router                    = google_compute_router.router2.name
  region                    = "us-central1"
  peer_ip_address           = "169.254.0.1"
  peer_asn                  = 64514
  advertised_route_priority = 100
  interface                 = google_compute_router_interface.router2_interface1.name
}

resource "google_compute_router_interface" "router2_interface2" {
  name       = "router2-interface2"
  router     = google_compute_router.router2.name
  region     = "us-central1"
  ip_range   = "169.254.1.1/30"
  vpn_tunnel = google_compute_vpn_tunnel.tunnel4.name
}

resource "google_compute_router_peer" "router2_peer2" {
  name                      = "router2-peer2"
  router                    = google_compute_router.router2.name
  region                    = "us-central1"
  peer_ip_address           = "169.254.1.2"
  peer_asn                  = 64514
  advertised_route_priority = 100
  interface                 = google_compute_router_interface.router2_interface2.name
}