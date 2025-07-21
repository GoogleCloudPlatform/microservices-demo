# crm.tf - GCP CRM Service Infrastructure

# Configure the Google Cloud provider
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.50.0"
    }
  }
}

variable "project_id" {
  description = "The GCP project ID where resources will be created"
  type        = string
}

provider "google" {
  project = var.project_id
  region  = "us-central1"
}

# Create a firewall rule to allow traffic on port 8080
resource "google_compute_firewall" "allow_crm_http" {
  name    = "tf-allow-crm-http"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  target_tags   = ["crm-server"]
  source_ranges = ["0.0.0.0/0"]
}

# Create the smallest possible Compute Engine VM instance
resource "google_compute_instance" "crm_mock_vm" {
  name         = "crm-mock-vm"
  machine_type = "e2-micro" # One of the smallest machine types available
  zone         = "us-central1-a"

  tags = ["crm-server"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral IP assigned automatically
    }
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
      
      console.log(`POST /customers - Added new customer: $${name} $${surname}`);
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

# Output the public IP address so we can test the service
output "instance_public_ip" {
  value       = google_compute_instance.crm_mock_vm.network_interface[0].access_config[0].nat_ip
  description = "The public IP address of the VM instance."
}

output "application_url" {
  value       = "http://${google_compute_instance.crm_mock_vm.network_interface[0].access_config[0].nat_ip}:8080/customers"
  description = "The URL to access the customers endpoint."
}