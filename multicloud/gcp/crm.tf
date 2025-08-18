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
  ip_cidr_range = "10.2.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.crm_vpc.id
  description   = "Subnet for CRM service"
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
  source_ranges = ["10.128.0.0/9", "10.2.0.0/24"]  # Online-boutique-vpc VPC and CRM VPC ranges
}

# Create the smallest possible Compute Engine VM instance
resource "google_compute_instance" "crm_vm" {
  name         = "crm-vm"
  machine_type = "e2-micro" # One of the smallest machine types available
  zone         = "us-central1-a"

  tags = ["crm-server"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.crm_vpc.id
    subnetwork = google_compute_subnetwork.crm_subnet.id
    // No access_config block = no external IP (private only)
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
      "name": "mock-crm-service",
      "version": "1.0.0",
      "main": "app.js",
      "dependencies": {
        "express": "^4.18.2"
      }
    }
    EOF

    # Create the app.js file with the mock CRM logic
    cat <<'EOF' > app.js
    const express = require('express');
    const app = express();
    const port = 8080;

    // Middleware to parse JSON bodies
    app.use(express.json());

    // In-memory data store with two hardcoded customers
    let customers = [
      { name: 'John', surname: 'Doe' },
      { name: 'Jane', surname: 'Smith' }
    ];

    // GET endpoint to list all customers
    app.get('/customers', (req, res) => {
      console.log('GET /customers - Returning customer list');
      res.status(200).json(customers);
    });

    // POST endpoint to add a new customer
    app.post('/customers', (req, res) => {
      const { name, surname } = req.body;

      if (!name || !surname) {
        console.log('POST /customers - Failed: Missing name or surname');
        return res.status(400).json({ error: 'Name and surname are required.' });
      }

      const newCustomer = { name, surname };
      customers.push(newCustomer);
      
      // Cleanup: Keep only the 10 most recent customers
      if (customers.length > 10) {
        const removedCount = customers.length - 10;
        customers = customers.slice(-10); // Keep last 10
        console.log(`POST /customers - Cleaned up $${removedCount} old customer(s), keeping 10 most recent`);
      }
      
      console.log(`POST /customers - Added new customer: $${name} $${surname}. Total: $${customers.length}`);
      res.status(201).json(newCustomer);
    });

    app.listen(port, '0.0.0.0', () => {
      console.log(`Mock CRM server listening on port $${port}`);
    });
    EOF

    # Install application dependencies
    npm install

    # Start the application using pm2 to run it in the background
    pm2 start app.js --name "crm-app"
  EOT
}

# Output the private IP address for internal communication
output "crm_service_url" {
  value       = "http://${google_compute_instance.crm_vm.network_interface[0].network_ip}:8080/customers"
  description = "The URL to access the CRM service via private IP."
}

output "crm_vm_private_ip" {
  value       = google_compute_instance.crm_vm.network_interface[0].network_ip
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

# 4. Create VPC peering from crm-vpc to online-boutique-vpc VPC
resource "google_compute_network_peering" "crm_to_ob" {
  name         = "crm-to-ob-peering"
  network      = google_compute_network.crm_vpc.id
  peer_network = "projects/${var.project_id}/global/networks/online-boutique-vpc"

  import_custom_routes = false
  export_custom_routes = false
}

# 5. Create VPC peering from online-boutique-vpc VPC to crm-vpc  
resource "google_compute_network_peering" "ob_to_crm" {
  name         = "ob-to-crm-peering"
  network      = "projects/${var.project_id}/global/networks/online-boutique-vpc"
  peer_network = google_compute_network.crm_vpc.id

  import_custom_routes = false
  export_custom_routes = false
}

# 6. Create VPC peering from remote VPC to online-boutique-vpc 
resource "google_compute_network_peering" "remote_to_ob" {
  name         = "remote-to-ob-peering"
  network      = "projects/${var.peering_project_id}/global/networks/${peering_vpc_network}"
  peer_network = "projects/${var.project_id}/global/networks/online-boutique-vpc"

  import_custom_routes = false
  export_custom_routes = false
}

# 7. Create VPC peering from online-boutique-vpc VPC to crm-vpc  
resource "google_compute_network_peering" "ob_to_remote" {
  name         = "ob-to-crm-peering"
  network      = "projects/${var.peering_project_id}/global/networks/online-boutique-vpc"
  peer_network = "projects/${var.peering_project_id}/global/networks/${peering_vpc_network}"

  import_custom_routes = false
  export_custom_routes = false
}