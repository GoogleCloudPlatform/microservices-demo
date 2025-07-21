# analytics.tf - Azure Analytics Service Infrastructure

# Configure Terraform providers for Azure and for generating a random password
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.1"
    }
  }
}

variable "subscription_id" {
  description = "The Azure subscription ID where resources will be created"
  type        = string
}

# Configure the Azure Provider
provider "azurerm" {
  subscription_id = var.subscription_id
  features {}
}

# 1. Create a resource group to hold all our resources
resource "azurerm_resource_group" "rg" {
  name     = "tf-analytics-service-rg"
  location = "West Europe" # You can change this to a region closer to you
}

# 2. Create the networking infrastructure
resource "azurerm_virtual_network" "vnet" {
  name                = "analytics-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "analytics-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "pip" {
  name                = "analytics-pip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# 3. Create a network security group (firewall) to allow HTTP on port 8080
resource "azurerm_network_security_group" "nsg" {
  name                = "analytics-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }
}

# 4. Create a network interface to connect the VM to the network
resource "azurerm_network_interface" "nic" {
  name                = "analytics-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip.id
  }
}

resource "azurerm_network_interface_security_group_association" "nsg_assoc" {
  network_interface_id      = azurerm_network_interface.nic.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

# Generate a random password for the VM admin user
resource "random_password" "password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# 5. Create the Linux Virtual Machine
resource "azurerm_linux_virtual_machine" "vm" {
  name                  = "analytics-service-vm"
  resource_group_name   = azurerm_resource_group.rg.name
  location              = azurerm_resource_group.rg.location
  size                  = "Standard_B1s" # A cheap, burstable VM size
  admin_username        = "azureuser"
  admin_password        = random_password.password.result
  disable_password_authentication = false

  network_interface_ids = [
    azurerm_network_interface.nic.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  # This startup script is Base64 encoded by Terraform and run on first boot
  custom_data = base64encode(<<-EOT
    #!/bin/bash
    
    sudo apt-get update
    sudo apt-get install -y nodejs npm
    sudo npm install pm2 -g
    
    sudo mkdir -p /opt/app
    sudo chown -R azureuser:azureuser /opt/app
    cd /opt/app

    cat <<'EOF' > package.json
    {
      "name": "mock-analytics-service",
      "version": "1.0.0",
      "main": "app.js",
      "dependencies": { "express": "^4.18.2" }
    }
    EOF

    cat <<'EOF' > app.js
    const express = require('express');
    const app = express();
    const port = 8080;

    app.use(express.json());

    // In-memory data store with two mocked metrics
    let metrics = [
      { transactionType: 'user_login', durationMs: 85, success: true, timestamp: '2025-07-21T07:15:00Z' },
      { transactionType: 'payment_processing', durationMs: 210, success: false, timestamp: '2025-07-21T07:16:30Z' }
    ];

    // POST endpoint to save a new transaction metric
    app.post('/metrics', (req, res) => {
      const { transactionType, durationMs, success } = req.body;

      if (typeof transactionType !== 'string' || typeof durationMs !== 'number' || typeof success !== 'boolean') {
        return res.status(400).json({ error: 'Invalid payload. Required fields: transactionType (string), durationMs (number), success (boolean).' });
      }

      const newMetric = { 
        transactionType, 
        durationMs, 
        success,
        timestamp: new Date().toISOString() // Add server-side timestamp
      };
      metrics.push(newMetric);
      
      // Cleanup: Keep only the 10 most recent metrics
      if (metrics.length > 10) {
        const removedCount = metrics.length - 10;
        metrics = metrics.slice(-10); // Keep last 10
        console.log(`POST /metrics - Cleaned up $${removedCount} old metric(s), keeping 10 most recent`);
      }
      
      console.log(`POST /metrics - Added new metric for $${transactionType} ($${durationMs}ms). Total: $${metrics.length}`);
      res.status(201).json(newMetric);
    });

    // GET endpoint to list all metrics and a summary
    app.get('/metrics', (req, res) => {
      if (metrics.length === 0) {
        return res.status(200).json({ summary: { totalTransactions: 0 }, data: [] });
      }

      const summary = {
        totalTransactions: metrics.length,
        successCount: metrics.filter(m => m.success).length,
        failureCount: metrics.filter(m => !m.success).length,
        averageDurationMs: Math.round(metrics.reduce((acc, m) => acc + m.durationMs, 0) / metrics.length)
      };
      
      console.log('GET /metrics - Returning summary and data');
      res.status(200).json({ summary, data: metrics });
    });

    app.listen(port, '0.0.0.0', () => {
      console.log(`Mock Analytics server listening on port $${port}`);
    });
    EOF

    npm install
    pm2 start app.js --name "analytics-app"
  EOT
  )
}

# 6. Output the public IP address and the full application URL
output "public_ip" {
  value       = azurerm_public_ip.pip.ip_address
  description = "The public IP address of the analytics server."
}

output "application_url" {
  value       = "http://${azurerm_public_ip.pip.ip_address}:8080/metrics"
  description = "The URL to access the metrics endpoint."
}