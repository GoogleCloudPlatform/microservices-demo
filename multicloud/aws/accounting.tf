# accounting.tf - AWS Accounting Service Infrastructure

# Configure the Terraform AWS provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1" # You can change this to any AWS region
}

# 1. Find the latest Ubuntu Server 22.04 LTS AMI.
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical's AWS account ID
}

# 2. Create a security group (firewall) to allow HTTP on port 8080.
resource "aws_security_group" "accounting_sg" {
  name        = "tf-accounting-server-sg"
  description = "Allow HTTP inbound traffic on port 8080"

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tf-accounting-server-sg"
  }
}

# 3. Create the EC2 instance (virtual machine).
resource "aws_instance" "accounting_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro" # Free-tier eligible

  # The startup script to install Node.js and run the app
  user_data = <<-EOT
    #!/bin/bash
    
    # Update packages and install Node.js and npm
    sudo apt-get update -y
    sudo apt-get install -y nodejs npm

    # Install pm2, a production process manager for Node.js
    sudo npm install pm2 -g

    # Create a directory for the app
    sudo mkdir -p /opt/app
    cd /opt/app

    # Create the package.json file
    cat <<'EOF' > package.json
    {
      "name": "mock-accounting-service",
      "version": "1.0.0",
      "main": "app.js",
      "dependencies": {
        "express": "^4.18.2"
      }
    }
    EOF

    # Create the app.js file with the mock accounting logic
    cat <<'EOF' > app.js
    const express = require('express');
    const app = express();
    const port = 8080;

    // Middleware to parse JSON bodies
    app.use(express.json());

    // In-memory data store with two hardcoded transactions
    let transactions = [
      { item: 'Office Supplies', price: 75.50, date: '2025-07-20' },
      { item: 'Software License', price: 299.99, date: '2025-07-21' }
    ];

    // GET endpoint to list all transactions
    app.get('/transactions', (req, res) => {
      console.log('GET /transactions - Returning transaction list');
      res.status(200).json(transactions);
    });

    // POST endpoint to add a new transaction
    app.post('/transactions', (req, res) => {
      const { item, price, date } = req.body;

      if (!item || !price || !date) {
        console.log('POST /transactions - Failed: Missing required fields');
        return res.status(400).json({ error: 'Fields item, price, and date are required.' });
      }

      const newTransaction = { item, price: parseFloat(price), date };
      transactions.push(newTransaction);
      
      console.log(`POST /transactions - Added new transaction: ${item}`);
      res.status(201).json(newTransaction);
    });

    app.listen(port, '0.0.0.0', () => {
      console.log(`Mock Accounting server listening on port ${port}`);
    });
    EOF

    # Install application dependencies
    npm install

    # Start the application using pm2 to run it in the background
    pm2 start app.js --name "accounting-app"
  EOT

  vpc_security_group_ids      = [aws_security_group.accounting_sg.id]
  associate_public_ip_address = true

  tags = {
    Name = "tf-accounting-server"
  }
}

# 4. Output the public IP address and full test URL.
output "public_ip" {
  value       = aws_instance.accounting_server.public_ip
  description = "The public IP address of the accounting server."
}

output "application_url" {
  value       = "http://${aws_instance.accounting_server.public_ip}:8080/transactions"
  description = "The URL to access the transactions endpoint."
}