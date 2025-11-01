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

# 2a. Create Cloud Router for NAT
resource "google_compute_router" "crm_router" {
  name    = "crm-router"
  region  = "asia-east1"
  network = google_compute_network.crm_vpc.id

  bgp {
    asn = 64514
  }
}

# 2b. Create Cloud NAT for internet access
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

# Create the smallest possible Compute Engine VM instance
resource "google_compute_instance" "crm_vm" {
  name         = "crm-vm"
  machine_type = "e2-micro" # One of the smallest machine types available
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

# 7. Create VPC peering from online-boutique-vpc VPC to remote  
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

# 8. Create CRM Frontend VM instance
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
    // No external IP - accessed via Load Balancer
  }

  # Startup script with embedded frontend application
  metadata_startup_script = <<-EOT
    #!/bin/bash
    
    # Update packages and install Node.js and npm
    sudo apt-get update
    sudo apt-get install -y nodejs npm
    
    # Install pm2, a production process manager for Node.js
    sudo npm install pm2 -g
    
    # Create a directory for the app
    sudo mkdir -p /opt/crm-frontend
    sudo chown -R $(whoami):$(whoami) /opt/crm-frontend
    cd /opt/crm-frontend
    
    # Create the package.json file
    cat <<'EOF' > package.json
    {
      "name": "crm-frontend",
      "version": "1.0.0",
      "description": "CRM Customer Dashboard Frontend",
      "main": "app.js",
      "dependencies": {
        "express": "^4.18.2"
      }
    }
    EOF
    
    # Create the frontend app.js file
    cat <<'APPJS' > app.js
    const express = require('express');
    const app = express();
    const port = 8080;

    app.get('/', (req, res) => {
      res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CRM Customer Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 0; }
            .container { max-width: 900px; }
            .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            .card-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px 15px 0 0 !important; padding: 20px; }
            .customer-card { transition: transform 0.2s, box-shadow 0.2s; border-left: 4px solid #667eea; }
            .customer-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            .customer-initials { width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; }
            .loading { text-align: center; padding: 40px; }
            .spinner-border { width: 3rem; height: 3rem; }
            .error-message { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 10px; margin: 20px 0; }
            .refresh-btn { transition: all 0.3s; }
            .refresh-btn:hover { transform: rotate(180deg); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h2 class="mb-1">CRM Customer Dashboard</h2>
                            <p class="mb-0 opacity-75">Live customer data from backend service</p>
                        </div>
                        <button onclick="loadCustomers()" class="btn btn-light refresh-btn" title="Refresh">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                                <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
                                <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div id="loading" class="loading">
                        <div class="spinner-border text-primary" role="status"></div>
                        <p class="mt-3 text-muted">Fetching customer data...</p>
                    </div>
                    <div id="error" class="error-message" style="display: none;"></div>
                    <div id="customers" style="display: none;">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="mb-0">Total Customers: <span id="customerCount" class="badge bg-primary">0</span></h5>
                            <small class="text-muted">Last updated: <span id="lastUpdate"></span></small>
                        </div>
                        <div id="customerList" class="row g-3"></div>
                    </div>
                </div>
            </div>
            <div class="text-center mt-4">
                <p class="text-white"><small>Backend API: <code id="backendUrl" class="text-white bg-dark px-2 py-1 rounded">Loading...</code></small></p>
            </div>
        </div>
        <script>
            const BACKEND_URL = 'http://10.3.0.2:8080/customers';
            document.getElementById('backendUrl').textContent = BACKEND_URL;
            
            function getInitials(name, surname) { return (name.charAt(0) + surname.charAt(0)).toUpperCase(); }
            
            function getRandomColor(name) {
                const colors = [
                    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
                ];
                return colors[name.charCodeAt(0) % colors.length];
            }
            
            function formatTime() { return new Date().toLocaleTimeString(); }
            
            async function loadCustomers() {
                const loadingEl = document.getElementById('loading');
                const errorEl = document.getElementById('error');
                const customersEl = document.getElementById('customers');
                
                loadingEl.style.display = 'block';
                errorEl.style.display = 'none';
                customersEl.style.display = 'none';
                
                try {
                    const response = await fetch(BACKEND_URL);
                    if (!response.ok) throw new Error(`HTTP error! status: $${response.status}`);
                    
                    const customers = await response.json();
                    document.getElementById('customerCount').textContent = customers.length;
                    document.getElementById('lastUpdate').textContent = formatTime();
                    
                    const customerList = document.getElementById('customerList');
                    customerList.innerHTML = '';
                    
                    if (customers.length === 0) {
                        customerList.innerHTML = '<div class="col-12 text-center py-5"><p class="text-muted">No customers found.</p></div>';
                    } else {
                        customers.forEach((customer, index) => {
                            const initials = getInitials(customer.name, customer.surname);
                            const bgGradient = getRandomColor(customer.name);
                            customerList.innerHTML += `
                                <div class="col-md-6">
                                    <div class="card customer-card h-100">
                                        <div class="card-body">
                                            <div class="d-flex align-items-center">
                                                <div class="customer-initials me-3" style="background: $${bgGradient}">$${initials}</div>
                                                <div class="flex-grow-1">
                                                    <h5 class="card-title mb-1">$${customer.name} $${customer.surname}</h5>
                                                    <p class="card-text text-muted mb-0"><small>Customer #$${index + 1}</small></p>
                                                </div>
                                                <div><span class="badge bg-success">Active</span></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                    }
                    
                    loadingEl.style.display = 'none';
                    customersEl.style.display = 'block';
                } catch (error) {
                    console.error('Error:', error);
                    loadingEl.style.display = 'none';
                    errorEl.style.display = 'block';
                    errorEl.innerHTML = '<strong>Error loading customers!</strong><br>' + error.message;
                }
            }
            
            loadCustomers();
            setInterval(loadCustomers, 30000);
        </script>
    </body>
    </html>
      `);
    });

    app.get('/health', (req, res) => {
      res.status(200).json({ status: 'healthy' });
    });

    app.listen(port, '0.0.0.0', () => {
      console.log(`CRM Frontend server listening on port $${port}`);
    });
    APPJS
    
    # Install application dependencies
    npm install
    
    # Start the application using pm2
    pm2 start app.js --name "crm-frontend"
    pm2 startup
    pm2 save
  EOT
}

# 9. Create instance group for the frontend VM
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

# 10. Create health check for frontend
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

# 11. Create backend service (using EXTERNAL_MANAGED for better configuration)
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

# 12. Create URL map
resource "google_compute_url_map" "crm_frontend_url_map" {
  name            = "crm-frontend-url-map"
  default_service = google_compute_backend_service.crm_frontend_backend.id
}

# 13. Create target HTTP proxy
resource "google_compute_target_http_proxy" "crm_frontend_proxy" {
  name    = "crm-frontend-http-proxy"
  url_map = google_compute_url_map.crm_frontend_url_map.id
}

# 14. Reserve a static external IP for the load balancer
resource "google_compute_global_address" "crm_frontend_ip" {
  name = "crm-frontend-lb-ip"
}

# 15. Create global forwarding rule (this is the external IP that users access)
resource "google_compute_global_forwarding_rule" "crm_frontend_forwarding_rule" {
  name                  = "crm-frontend-forwarding-rule"
  target                = google_compute_target_http_proxy.crm_frontend_proxy.id
  port_range            = "80"
  ip_address            = google_compute_global_address.crm_frontend_ip.address
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# 16. Firewall rule to allow health checks from Google Cloud load balancers
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

# 17. Firewall rule to allow HTTP traffic from load balancer to frontend instances
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

# 18. Firewall rule to allow frontend to communicate with backend
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
  value       = google_compute_instance.crm_frontend_vm.network_interface[0].network_ip
  description = "Private IP address of the CRM frontend VM"
}