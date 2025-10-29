# Accounting Service

A REST API service for managing accounting transactions, designed to run on Google Cloud Run. This service integrates with the CRM Service to retrieve customer information.

## Features

- RESTful API for transaction management
- Automatic CRM integration for customer data retrieval
- Cloud Run deployment ready
- Container-based deployment with Cloud Build
- VPC Connector for private CRM service access

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /transactions` - List all transactions (also calls CRM Service to get customers)
- `GET /transactions/:id` - Get a specific transaction
- `POST /transactions` - Add a new transaction
- `PUT /transactions/:id` - Update a transaction
- `DELETE /transactions/:id` - Delete a transaction

## Environment Variables

- `PORT` - Server port (default: 8080)
- `CRM_SERVICE_URL` - URL of the CRM service (optional, for CRM integration)

## Local Development

```bash
npm install
npm start
```

The service will be available at `http://localhost:8080`

### Testing with CRM Integration

To test the CRM integration locally:

```bash
export CRM_SERVICE_URL=http://your-crm-service:8080
npm start
```

## Building and Deploying

### Prerequisites

1. Create an Artifact Registry repository:
```bash
gcloud artifacts repositories create accounting-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Accounting service container images"
```

2. Enable required APIs:
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable vpcaccess.googleapis.com
```

### Build and Push to Artifact Registry

From the `multicloud/gcp/accounting-service` directory:

```bash
# Submit build to Cloud Build
gcloud builds submit --config=cloudbuild.yaml

# Or build manually
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/accounting-repo/accounting-service:latest .
docker push us-central1-docker.pkg.dev/PROJECT_ID/accounting-repo/accounting-service:latest
```

### Deploy with Terraform

From the `multicloud/gcp` directory:

```bash
terraform init
terraform apply
```

The terraform configuration will:
- Enable necessary Google Cloud APIs
- Create VPC Connector for CRM access
- Deploy the container to Cloud Run
- Configure public access
- Output the service URL

## Network Configuration

This service uses a **VPC Connector** (not Direct VPC egress) to connect to the CRM service in `crm-vpc`:

- **Accounting Service**: Cloud Run with VPC Connector
- **CRM Service**: Running on VM in private `crm-vpc` (10.2.0.0/24)
- **Connectivity**: VPC Connector creates a managed connection to the CRM VPC
- **Firewall**: Configured to allow traffic from VPC Connector IP range to CRM service

### VPC Connector vs Direct VPC Egress

- **VPC Connector**: Serverless VPC Access connector (used here)
  - Managed by Google
  - Separate IP range from target VPC
  - Good for occasional access
  
- **Direct VPC egress**: Cloud Run instances in VPC subnet (food service uses this)
  - Instances get IPs from VPC subnet
  - Better for frequent internal communication
  - Lower latency

## Response Format

When calling `GET /transactions`, the response includes:

```json
{
  "transactions": [
    {
      "id": 1,
      "item": "Office Supplies",
      "price": 75.50,
      "date": "2025-07-20",
      "customer": "Acme Corp"
    }
  ],
  "crmIntegration": {
    "connected": true,
    "customers": [
      { "name": "John", "surname": "Doe" },
      { "name": "Jane", "surname": "Smith" }
    ],
    "timestamp": "2025-10-29T00:00:00.000Z"
  },
  "summary": {
    "totalTransactions": 4,
    "totalAmount": "2025.49"
  }
}
```

## Testing

```bash
# Health check
curl https://ACCOUNTING_SERVICE_URL/health

# Get all transactions (with CRM integration)
curl https://ACCOUNTING_SERVICE_URL/transactions

# Add a new transaction
curl -X POST https://ACCOUNTING_SERVICE_URL/transactions \
  -H "Content-Type: application/json" \
  -d '{"item":"New Item","price":100.50,"date":"2025-10-29","customer":"Test Corp"}'

# Get specific transaction
curl https://ACCOUNTING_SERVICE_URL/transactions/1

# Update transaction
curl -X PUT https://ACCOUNTING_SERVICE_URL/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"price":120.00}'

# Delete transaction
curl -X DELETE https://ACCOUNTING_SERVICE_URL/transactions/1
```

