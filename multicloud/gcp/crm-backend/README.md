# CRM Backend Service

Mock CRM backend service providing customer data management.

## Features

- **GET /customers**: Returns list of all customers
- **POST /customers**: Add a new customer (requires name and surname)
- **Auto-cleanup**: Keeps only the 10 most recent customers
- **In-memory storage**: Data resets on service restart

## API Endpoints

### GET /customers

Returns an array of customer objects.

**Response:**
```json
[
  { "name": "John", "surname": "Doe" },
  { "name": "Jane", "surname": "Smith" }
]
```

### POST /customers

Add a new customer.

**Request:**
```json
{
  "name": "Alice",
  "surname": "Johnson"
}
```

**Response:**
```json
{
  "name": "Alice",
  "surname": "Johnson"
}
```

## Architecture

The CRM backend runs on a private VM with no external IP:
- **Internal IP**: 10.3.0.2 (static)
- **Port**: 8080
- **Network**: crm-vpc
- **Access**: Via VPC peering from online-boutique-vpc or from other VMs in crm-vpc

## Local Development

```bash
npm install
npm start
```

Server runs on `http://localhost:8080`

## Deployment

Deployed via Terraform (`crm.tf`):
1. VM instance created with startup script
2. Script installs Node.js, npm, and pm2
3. Application code embedded in startup script
4. pm2 manages the Node.js process

## Tech Stack

- **Runtime**: Node.js
- **Framework**: Express
- **Process Manager**: pm2
- **OS**: Debian 11

