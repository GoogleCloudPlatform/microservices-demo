# inventory.tf - GCP Inventory Service with Private IP and PSC
# Note: Uses shared terraform, variable, and provider configurations from main.tf

# 1. Create a dedicated VPC network for the inventory service
resource "google_compute_network" "inventory_vpc" {
  name                    = "inventory-vpc"
  auto_create_subnetworks = false
  description             = "Dedicated VPC for inventory service"
}

# 2. Create a subnet in the inventory VPC
resource "google_compute_subnetwork" "inventory_subnet" {
  name          = "inventory-subnet"
  ip_cidr_range = "10.1.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.inventory_vpc.id
  description   = "Subnet for inventory service"
}

# 2b. Create a dedicated subnet for PSC
resource "google_compute_subnetwork" "inventory_psc_subnet" {
  name          = "inventory-psc-subnet"
  ip_cidr_range = "10.1.1.0/24"
  region        = "us-central1"
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
  
  source_ranges = ["10.1.0.0/24", "10.0.0.0/8"]
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
  machine_type = "e2-micro"
  zone         = "us-central1-a"
  
  tags = ["inventory-server"]
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }
  
  # Network interface with private IP only (no external IP)
  network_interface {
    network    = google_compute_network.inventory_vpc.id
    subnetwork = google_compute_subnetwork.inventory_subnet.id
    # No access_config block = no external IP
  }
  
  # Service account for VM
  service_account {
    scopes = ["cloud-platform"]
  }
  
  # Startup script to install and run the inventory service
  metadata_startup_script = <<-EOT
    #!/bin/bash
    set -e
    
    # Update system
    apt-get update
    apt-get install -y curl
    
    # Install Node.js
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
    
    # Install PM2 for process management
    npm install -g pm2
    
    # Create application directory
    mkdir -p /opt/inventory-service
    cd /opt/inventory-service
    
    # Create package.json
    cat > package.json << 'EOF'
{
  "name": "inventory-service",
  "version": "1.0.0",
  "description": "Simple inventory management service",
  "main": "app.js",
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF
    
    # Create the main application file
    cat > app.js << 'EOF'
const express = require('express');
const app = express();
const port = 8080;

app.use(express.json());

// In-memory inventory data (simulating a database)
let inventory = [
  { productId: "OLJCESPC7Z", name: "Vintage Typewriter", stockLevel: 45, reserved: 3, available: 42 },
  { productId: "66VCHSJNUP", name: "Vintage Camera Lens", stockLevel: 12, reserved: 0, available: 12 },
  { productId: "1YMWWN1N4O", name: "Home Barista Kit", stockLevel: 8, reserved: 2, available: 6 },
  { productId: "L9ECAV7KIM", name: "Terrarium", stockLevel: 25, reserved: 1, available: 24 },
  { productId: "2ZYFJ3GM2N", name: "Film Camera", stockLevel: 15, reserved: 0, available: 15 },
  { productId: "0PUK6V6EV0", name: "Vintage Record Player", stockLevel: 3, reserved: 1, available: 2 },
  { productId: "LS4PSXUNUM", name: "Metal Camping Mug", stockLevel: 100, reserved: 5, available: 95 },
  { productId: "9SIQT8TOJO", name: "City Bike", stockLevel: 7, reserved: 0, available: 7 },
  { productId: "6E92ZMYYFZ", name: "Air Plant", stockLevel: 30, reserved: 2, available: 28 }
];

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'inventory', timestamp: new Date().toISOString() });
});

// Get all inventory
app.get('/inventory', (req, res) => {
  console.log('GET /inventory - Retrieved all inventory items');
  res.json({
    total: inventory.length,
    data: inventory.map(item => ({
      ...item,
      lastUpdated: new Date().toISOString()
    }))
  });
});

// Get inventory for specific product
app.get('/inventory/:productId', (req, res) => {
  const { productId } = req.params;
  const item = inventory.find(i => i.productId === productId);
  
  if (!item) {
    console.log(`GET /inventory/$${productId} - Product not found`);
    return res.status(404).json({ error: 'Product not found' });
  }
  
  console.log(`GET /inventory/$${productId} - Retrieved inventory for $${item.name}`);
  res.json({
    ...item,
    lastUpdated: new Date().toISOString()
  });
});

// Reserve stock for a product
app.post('/inventory/:productId/reserve', (req, res) => {
  const { productId } = req.params;
  const { quantity = 1 } = req.body;
  
  const item = inventory.find(i => i.productId === productId);
  
  if (!item) {
    console.log(`POST /inventory/$${productId}/reserve - Product not found`);
    return res.status(404).json({ error: 'Product not found' });
  }
  
  if (item.available < quantity) {
    console.log(`POST /inventory/$${productId}/reserve - Insufficient stock. Available: $${item.available}, Requested: $${quantity}`);
    return res.status(400).json({ 
      error: 'Insufficient stock', 
      available: item.available, 
      requested: quantity 
    });
  }
  
  // Reserve the stock
  item.reserved += quantity;
  item.available -= quantity;
  
  console.log(`POST /inventory/$${productId}/reserve - Reserved $${quantity} units of $${item.name}. Available: $${item.available}, Reserved: $${item.reserved}`);
  res.json({
    message: 'Stock reserved successfully',
    productId: productId,
    reservedQuantity: quantity,
    ...item,
    lastUpdated: new Date().toISOString()
  });
});

// Release reserved stock
app.post('/inventory/:productId/release', (req, res) => {
  const { productId } = req.params;
  const { quantity = 1 } = req.body;
  
  const item = inventory.find(i => i.productId === productId);
  
  if (!item) {
    console.log(`POST /inventory/$${productId}/release - Product not found`);
    return res.status(404).json({ error: 'Product not found' });
  }
  
  if (item.reserved < quantity) {
    console.log(`POST /inventory/$${productId}/release - Insufficient reserved stock. Reserved: $${item.reserved}, Requested: $${quantity}`);
    return res.status(400).json({ 
      error: 'Insufficient reserved stock', 
      reserved: item.reserved, 
      requested: quantity 
    });
  }
  
  // Release the stock
  item.reserved -= quantity;
  item.available += quantity;
  
  console.log(`POST /inventory/$${productId}/release - Released $${quantity} units of $${item.name}. Available: $${item.available}, Reserved: $${item.reserved}`);
  res.json({
    message: 'Stock released successfully',
    productId: productId,
    releasedQuantity: quantity,
    ...item,
    lastUpdated: new Date().toISOString()
  });
});

// Update stock levels (admin endpoint)
app.put('/inventory/:productId', (req, res) => {
  const { productId } = req.params;
  const { stockLevel } = req.body;
  
  if (typeof stockLevel !== 'number' || stockLevel < 0) {
    console.log(`PUT /inventory/$${productId} - Invalid stock level: $${stockLevel}`);
    return res.status(400).json({ error: 'Valid stock level required' });
  }
  
  const item = inventory.find(i => i.productId === productId);
  
  if (!item) {
    console.log(`PUT /inventory/$${productId} - Product not found`);
    return res.status(404).json({ error: 'Product not found' });
  }
  
  const oldStock = item.stockLevel;
  item.stockLevel = stockLevel;
  item.available = stockLevel - item.reserved;
  
  console.log(`PUT /inventory/$${productId} - Updated $${item.name} stock from $${oldStock} to $${stockLevel}. Available: $${item.available}`);
  res.json({
    message: 'Stock updated successfully',
    ...item,
    lastUpdated: new Date().toISOString()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Inventory service listening on port $${port}`);
  console.log(`Initialized with $${inventory.length} products in inventory`);
});
EOF
    
    # Install dependencies
    npm install
    
    # Start the application with PM2
    pm2 start app.js --name "inventory-service"
    pm2 startup
    pm2 save
    
    echo "Inventory service started successfully"
  EOT
}

# 6. Create PSC service attachment (expose inventory service via PSC)
resource "google_compute_service_attachment" "inventory_psc_attachment" {
  name        = "inventory-psc-attachment"
  region      = "us-central1"
  description = "PSC attachment for inventory service"
  
  # Enable PSC
  enable_proxy_protocol    = false
  connection_preference    = "ACCEPT_MANUAL"
  
  # Connect to the PSC subnet
  nat_subnets = [google_compute_subnetwork.inventory_psc_subnet.id]
  
  # Target service (we'll use a load balancer)
  target_service = google_compute_forwarding_rule.inventory_forwarding_rule.id
  
  # Allow connections from the default VPC project
  consumer_accept_lists {
    project_id_or_num = var.project_id
    connection_limit  = 10
  }
}

# 7. Create internal load balancer for the inventory service
resource "google_compute_forwarding_rule" "inventory_forwarding_rule" {
  name   = "inventory-forwarding-rule"
  region = "us-central1"
  
  load_balancing_scheme = "INTERNAL"
  backend_service       = google_compute_region_backend_service.inventory_backend.id
  all_ports            = true
  network              = google_compute_network.inventory_vpc.id
  subnetwork           = google_compute_subnetwork.inventory_subnet.id
}

# 8. Create backend service
resource "google_compute_region_backend_service" "inventory_backend" {
  name   = "inventory-backend-service"
  region = "us-central1"
  
  health_checks = [google_compute_region_health_check.inventory_health_check.id]
  
  backend {
    group          = google_compute_instance_group.inventory_instance_group.id
    balancing_mode = "CONNECTION"
  }
}

# 9. Create instance group
resource "google_compute_instance_group" "inventory_instance_group" {
  name = "inventory-instance-group"
  zone = "us-central1-a"
  
  instances = [google_compute_instance.inventory_vm.id]
  
  named_port {
    name = "http"
    port = "8080"
  }
}

# 10. Create health check
resource "google_compute_region_health_check" "inventory_health_check" {
  name   = "inventory-health-check"
  region = "us-central1"
  
  timeout_sec        = 5
  check_interval_sec = 10
  
  http_health_check {
    port         = "8080"
    request_path = "/health"
  }
}

# 11. Create PSC endpoint in the default network (for connecting to inventory service)
resource "google_compute_forwarding_rule" "inventory_psc_endpoint" {
  name   = "inventory-psc-endpoint"
  region = "us-central1"
  
  load_balancing_scheme = ""
  target                = google_compute_service_attachment.inventory_psc_attachment.id
  network               = "default"  # Connect from default network
  
  # This will get an IP in the default network that can reach the inventory service
}

# Outputs
output "inventory_vm_private_ip" {
  value       = google_compute_instance.inventory_vm.network_interface[0].network_ip
  description = "The private IP address of the inventory VM"
}

output "inventory_psc_endpoint_ip" {
  value       = google_compute_forwarding_rule.inventory_psc_endpoint.ip_address
  description = "The PSC endpoint IP address accessible from default network"
}

output "inventory_service_url" {
  value       = "http://${google_compute_forwarding_rule.inventory_psc_endpoint.ip_address}:8080/inventory"
  description = "The URL to access the inventory service via PSC from default network"
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