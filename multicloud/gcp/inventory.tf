# inventory.tf - GCP Inventory Service with Private IP and PSC
# Note: Uses shared terraform, variable, and provider configurations from main.tf

# Data source to get the default subnet in europe-west1 (where GKE cluster is located)
data "google_compute_subnetwork" "default_subnet_europe" {
  name   = "online-boutique-vpc"
  region = "europe-west1"
}

# 1. Create a dedicated VPC network for the inventory service
resource "google_compute_network" "inventory_vpc" {
  name                    = "inventory-vpc"
  auto_create_subnetworks = false
  description             = "Dedicated VPC for inventory service"
}

# 2. Create a subnet in the inventory VPC
resource "google_compute_subnetwork" "inventory_subnet" {
  name          = "inventory-subnet"
  ip_cidr_range = "10.20.0.0/24"
  region        = "europe-west1"
  network       = google_compute_network.inventory_vpc.id
  description   = "Subnet for inventory service"
}

# 2b. Create a dedicated subnet for PSC
resource "google_compute_subnetwork" "inventory_psc_subnet" {
  name          = "inventory-psc-subnet"
  ip_cidr_range = "10.20.1.0/24"
  region        = "europe-west1"
  network       = google_compute_network.inventory_vpc.id
  purpose       = "PRIVATE_SERVICE_CONNECT"
  description   = "Subnet for PSC service attachment"
}

# 3. Create firewall rules for the inventory VPC
resource "google_compute_firewall" "inventory_internal" {
  name    = "inventory-allow-internal"
  network = google_compute_network.inventory_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["8080", "22", "80", "443"]
  }
  
  allow {
    protocol = "icmp"
  }
  
  source_ranges = ["10.0.0.0/8", "10.10.0.0/24", "10.128.0.0/24", "10.132.0.0/24", "130.211.0.0/22", "35.191.0.0/16"]
  description   = "Allow internal traffic within inventory VPC and from PSC"
}

# 4. Create firewall rule for PSC connectivity
resource "google_compute_firewall" "inventory_psc" {
  name    = "inventory-allow-psc"
  network = google_compute_network.inventory_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }
  
  source_ranges = ["35.199.192.0/19"]  # PSC source range
  description   = "Allow PSC connectivity to inventory service"
}

# 5. Create the inventory service VM with private IP only
resource "google_compute_instance" "inventory_vm" {
  name         = "inventory-service-vm"
  machine_type = "e2-small"
  zone         = "europe-west1-b"
  
  tags = ["inventory-server"]
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }
  
  # Network interface with private IP only (no external IP)
  network_interface {
    network    = google_compute_network.inventory_vpc.id
    subnetwork = google_compute_subnetwork.inventory_subnet.id
    # No access_config block = no external IP
  }
  
  # Startup script to install and run the inventory service
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
      "name": "mock-inventory-service",
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

    // In-memory data store
    let items = [
    ];

    // GET endpoint to list all items
    app.get('/inventory', (req, res) => {
      console.log('GET /inventory - Returning items list');
      res.status(200).json(items);
    });

    // POST endpoint to add a new item
    app.post('/inventory', (req, res) => {
      const { name, code } = req.body;

      if (!name || !code) {
        console.log('POST /furniture - Failed: Missing name or code');
        return res.status(400).json({ error: 'Name and code are required.' });
      }
      const index = items.findIndex(el => el.code === code);
      if (index >-1) {
        items[index].count++;
      } else {
        items.push({name, code, count: 1 });
      }
      
      // Cleanup: Keep only the 10 most recent items
      if (items.length > 10) {
        const removedCount = items.length - 10;
        items = items.slice(-10); // Keep last 10
        console.log(`POST /furniture - Cleaned up $${removedCount} old items(s), keeping 10 most recent`);
      }
      
      console.log(`POST /inventory - Added new iten: $${name} $${code}. Total: $${items.length}`);
      res.status(201).json(newItem);
    });

    app.listen(port, '0.0.0.0', () => {
      console.log(`Mock inventory server listening on port $${port}`);
    });
    EOF

    # Install application dependencies
    npm install

    # Start the application using pm2 to run it in the background
    pm2 start app.js --name "crm-app"
  EOT
}

# 6. Create PSC service attachment (expose inventory service via PSC)
resource "google_compute_service_attachment" "inventory_psc_attachment" {
  name        = "inventory-psc-attachment"
  region      = "europe-west1"
  description = "PSC attachment for inventory service"
  
  # Enable PSC
  enable_proxy_protocol    = false
  connection_preference    = "ACCEPT_MANUAL"
  
  # Connect to the PSC subnet
  nat_subnets = [google_compute_subnetwork.inventory_psc_subnet.id]
  
  # Target service (we'll use a load balancer)
  target_service = google_compute_forwarding_rule.inventory_forwarding_rule.id
  
  # Allow connections from the online-boutique-vpc VPC project
  consumer_accept_lists {
    project_id_or_num = var.project_id
    connection_limit  = 10
  }
}

# 7. Create internal load balancer for the inventory service
resource "google_compute_forwarding_rule" "inventory_forwarding_rule" {
  name   = "inventory-forwarding-rule"
  region = "europe-west1"
  load_balancing_scheme = "INTERNAL"
  backend_service       = google_compute_region_backend_service.inventory_backend.id
  all_ports            = true
  network              = google_compute_network.inventory_vpc.id
  subnetwork           = google_compute_subnetwork.inventory_subnet.id
}

# 8. Create backend service
resource "google_compute_region_backend_service" "inventory_backend" {
  name   = "inventory-backend-service"
  region = "europe-west1"
  
  health_checks = [google_compute_region_health_check.inventory_health_check.id]
  
  backend {
    group          = google_compute_instance_group.inventory_instance_group.id
    balancing_mode = "CONNECTION"
  }
}

# 9. Create instance group
resource "google_compute_instance_group" "inventory_instance_group" {
  name = "inventory-instance-group"
  zone = "europe-west1-b"
  
  instances = [google_compute_instance.inventory_vm.id]
  
  named_port {
    name = "http"
    port = "8080"
  }
}

# 10. Create health check
resource "google_compute_region_health_check" "inventory_health_check" {
  name   = "inventory-health-check"f
  region = "europe-west1"
  
  timeout_sec        = 5
  check_interval_sec = 10
  
  http_health_check {
    port         = "8080"
    request_path = "/health"
  }
}

# 11. Reserve an IP address for the PSC endpoint in europe-west1
resource "google_compute_address" "inventory_psc_ip_europe" {
  name         = "inventory-psc-ip-europe"
  region       = "europe-west1"
  subnetwork   = data.google_compute_subnetwork.default_subnet_europe.id
  address_type = "INTERNAL"
  description  = "Reserved IP for inventory PSC endpoint in europe-west1"
}

# 12. Create PSC endpoint in europe-west1 (where GKE cluster is located)
resource "google_compute_forwarding_rule" "inventory_psc_endpoint_europe" {
  name   = "inventory-psc-endpoint-europe"
  region = "europe-west1"
  allow_psc_global_access = true
  load_balancing_scheme   = ""
  target                = google_compute_service_attachment.inventory_psc_attachment.id
  network               = "online-boutique-vpc"  # Connect from online-boutique-vpc network
  ip_address            = google_compute_address.inventory_psc_ip_europe.self_link
  
  # This provides PSC access from europe-west1 region and as it is global, gke cluster from u-central1 should be able to access it
}

# Outputs
output "inventory_vm_private_ip" {
  value       = google_compute_instance.inventory_vm.network_interface[0].network_ip
  description = "The private IP address of the inventory VM"
}

output "inventory_psc_endpoint_ip_europe" {
  value       = google_compute_address.inventory_psc_ip_europe.address
  description = "The PSC endpoint IP address in europe-west1 region"
}

output "inventory_service_url_europe" {
  value       = "http://${google_compute_address.inventory_psc_ip_europe.address}:8080/inventory"
  description = "The URL to access the inventory service via PSC from europe-west1 region"
}

output "inventory_vpc_name" {
  value       = google_compute_network.inventory_vpc.name
  description = "The name of the inventory VPC network"
}

output "inventory_subnet_cidr" {
  value       = google_compute_subnetwork.inventory_subnet.ip_cidr_range
  description = "The CIDR range of the inventory subnet"
}

output "inventory_psc_subnet_cidr" {
  value       = google_compute_subnetwork.inventory_psc_subnet.ip_cidr_range
  description = "The CIDR range of the PSC subnet"
}

 
