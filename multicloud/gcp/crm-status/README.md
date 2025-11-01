# CRM Status Monitor

Public-facing status monitoring dashboard for the CRM backend service. This VM demonstrates direct internet-to-VM connectivity.

## Features

- **Real-time Monitoring**: Check CRM backend service health on-demand
- **Response Time**: Measures API response time in milliseconds
- **HTTP Status**: Displays HTTP status code from backend
- **Customer Count**: Shows number of customers in the system
- **Manual Refresh**: No auto-refresh - user-initiated checks only
- **Public Access**: Accessible directly from the internet via static public IP

## Architecture

```
Internet → crm-public-status-vm:80 (public IP: static)
              ↓
           crm-backend-vm:8080 (10.3.0.2 static private IP)
```

## Network Configuration

- **Internal IP**: 10.3.0.4 (static)
- **External IP**: Static public IP (assigned by Terraform)
- **Port**: 80 (HTTP)
- **Network**: crm-vpc
- **Subnet**: crm-subnet (10.3.0.0/24)

## Monitored Endpoint

- **Backend URL**: `http://10.3.0.2:8080/customers`
- **Method**: GET
- **Expected Response**: JSON array of customer objects

## Status Display

The dashboard shows:
1. **Service Status**: Operational (green) / Degraded (orange) / Unavailable (red)
2. **HTTP Status Code**: 200, 404, 500, etc.
3. **Response Time**: In milliseconds, color-coded by performance
4. **Customer Count**: Number of customers from backend response
5. **Last Check Timestamp**: When the status was last checked

## Local Development

```bash
npm install
sudo npm start  # Requires sudo for port 80
```

Server runs on `http://localhost:80`

**Note**: Running on port 80 requires root/sudo privileges. For development, you may want to change the port to 8080 in `app.js`.

## Deployment

Deployed via Terraform (`crm.tf`):
1. VM instance created with both static internal and external IPs
2. Startup script referenced from `startup.sh` file
3. Script installs Node.js, npm, and pm2
4. Application code embedded in startup script
5. Firewall rule allows HTTP traffic from internet (0.0.0.0/0)
6. pm2 manages the Node.js process

## Firewall Rules

Two firewall rules enable this VM:
1. **Internet → Status VM**: Allow port 80 from 0.0.0.0/0 to `crm-status` tag
2. **Status VM → Backend**: Allow port 8080 from `crm-status` tag to `crm-server` tag

## Use Case

This VM demonstrates:
- **Direct Internet Access**: Shows VM with public IP accessible from anywhere
- **VM-to-VM Communication**: Status VM calls backend VM within the same VPC
- **Static IP Benefits**: Both IPs are static, ensuring consistent connectivity

Perfect for demonstrating how traffic flows directly to a VM without load balancers.

## Tech Stack

- **Runtime**: Node.js
- **Framework**: Express
- **UI**: Bootstrap 5 + Vanilla JavaScript
- **Process Manager**: pm2
- **OS**: Debian 11

