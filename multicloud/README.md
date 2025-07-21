# Multicloud Infrastructure Documentation

This folder contains Terraform configurations that deploy mock services across three major cloud providers: AWS, Azure, and Google Cloud Platform. Each service exposes RESTful APIs for different business functions.

## Architecture Overview

The multicloud setup demonstrates how to deploy services across different cloud platforms with various networking configurations:

- **AWS**: Accounting Service (Financial transactions) - Public IP
- **Azure**: Analytics Service (Performance metrics) - Public IP
- **GCP**: CRM Service (Customer relationship management) - Public IP  
- **GCP**: Inventory Service (Stock management) - Private IP only with PSC

**Network Architecture**:
- **Public services**: AWS, Azure, and GCP CRM services with external IPs
- **Private service**: GCP Inventory service in dedicated VPC (inventory-vpc) 
- **PSC connectivity**: Secure private connection from default VPC to inventory VPC
- **Service isolation**: Each service demonstrates different security patterns

All services run Node.js applications on port 8080 with RESTful APIs.

## Services Overview

### 1. AWS Accounting Service (`aws/accounting.tf`)

**Purpose**: Manages financial transaction records  
**Cloud Provider**: Amazon Web Services  
**Instance**: EC2 t2.micro (free-tier eligible)  
**Region**: us-east-1  

#### Infrastructure Components
- EC2 instance with Ubuntu 22.04 LTS
- Security group allowing HTTP traffic on port 8080
- Automated Node.js application deployment via user_data script

#### REST API Contract

**Base URL**: `http://<public-ip>:8080`

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/transactions` | List all transactions | None | Array of transaction objects |
| POST | `/transactions` | Add new transaction | `{"item": "string", "price": number, "date": "YYYY-MM-DD"}` | Created transaction object |

**Sample Data**:
```json
[
  { "item": "Office Supplies", "price": 75.50, "date": "2025-07-20" },
  { "item": "Software License", "price": 299.99, "date": "2025-07-21" }
]
```

**Error Responses**:
- `400 Bad Request`: Missing required fields (item, price, date)

### 2. Azure Analytics Service (`azure/analytics.tf`)

**Purpose**: Collects and analyzes transaction performance metrics  
**Cloud Provider**: Microsoft Azure  
**Instance**: Standard_B1s (burstable performance)  
**Region**: West Europe  

#### Infrastructure Components
- Linux Virtual Machine with Ubuntu 22.04 LTS
- Virtual Network with dedicated subnet
- Network Security Group allowing HTTP traffic on port 8080
- Public IP with static allocation
- Secure password generation for VM access

#### REST API Contract

**Base URL**: `http://<public-ip>:8080`

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/metrics` | Get metrics summary and data | None | Object with summary stats and metrics array |
| POST | `/metrics` | Record new metric | `{"transactionType": "string", "durationMs": number, "success": boolean}` | Created metric with timestamp |

**Sample Response Structure**:
```json
{
  "summary": {
    "totalTransactions": 2,
    "successCount": 1,
    "failureCount": 1,
    "averageDurationMs": 148
  },
  "data": [
    {
      "transactionType": "user_login",
      "durationMs": 85,
      "success": true,
      "timestamp": "2025-07-21T07:15:00Z"
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid payload structure or data types

### 3. GCP CRM Service (`gcp/crm.tf`)

**Purpose**: Manages customer relationship data  
**Cloud Provider**: Google Cloud Platform  
**Instance**: e2-micro (smallest available)  
**Region**: us-central1  

#### Infrastructure Components
- Compute Engine instance with Debian 11
- Firewall rule allowing HTTP traffic on port 8080
- Automated Node.js application deployment via startup script

### 4. GCP Inventory Service (`gcp/inventory.tf`)

**Purpose**: Manages product stock levels, reservations, and availability  
**Cloud Provider**: Google Cloud Platform  
**Instance**: e2-micro (private IP only)  
**Region**: us-central1  

#### Infrastructure Components
- Dedicated VPC network (inventory-vpc) with 10.1.0.0/24 subnet
- VM with private IP only (no external IP access)
- Private Service Connect (PSC) for secure connectivity from default VPC
- Internal load balancer with health checks
- Firewall rules for internal and PSC traffic

#### Security Features
- **Private IP only**: VM has no external IP address
- **Network isolation**: Separate VPC for inventory data
- **PSC connectivity**: Secure private connection to default network
- **Controlled access**: Firewall rules restrict traffic to necessary ports

#### REST API Contract

**Base URL**: `http://<public-ip>:8080`

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/customers` | List all customers | None | Array of customer objects |
| POST | `/customers` | Add new customer | `{"name": "string", "surname": "string"}` | Created customer object |

**Sample Data**:
```json
[
  { "name": "John", "surname": "Doe" },
  { "name": "Jane", "surname": "Smith" }
]
```

**Error Responses**:
- `400 Bad Request`: Missing name or surname fields

#### REST API Contract (Inventory Service)

**Base URL**: `http://<psc-endpoint-ip>:8080` (accessible via PSC from default VPC)

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/inventory` | List all product stock levels | None | Object with total count and inventory array |
| GET | `/inventory/{productId}` | Get stock for specific product | None | Product inventory object |
| POST | `/inventory/{productId}/reserve` | Reserve stock for purchase | `{"quantity": number}` | Updated inventory with reservation |
| POST | `/inventory/{productId}/release` | Release reserved stock | `{"quantity": number}` | Updated inventory after release |
| PUT | `/inventory/{productId}` | Update stock levels | `{"stockLevel": number}` | Updated inventory object |
| GET | `/health` | Health check endpoint | None | Service status |

**Sample Response Structure**:
```json
{
  "total": 9,
  "data": [
    {
      "productId": "OLJCESPC7Z",
      "name": "Vintage Typewriter", 
      "stockLevel": 45,
      "reserved": 3,
      "available": 42,
      "lastUpdated": "2025-01-20T10:30:00Z"
    }
  ]
}
```

**Sample Product IDs** (matching Online Boutique catalog):
- `OLJCESPC7Z` - Vintage Typewriter
- `66VCHSJNUP` - Vintage Camera Lens  
- `1YMWWN1N4O` - Home Barista Kit
- `L9ECAV7KIM` - Terrarium
- `2ZYFJ3GM2N` - Film Camera

**Error Responses**:
- `400 Bad Request`: Invalid quantity or stock level
- `404 Not Found`: Product not found

## Deployment Instructions

### Prerequisites

1. **Terraform**: Install Terraform >= 1.0
2. **Cloud CLI Tools**: 
   - AWS CLI configured with credentials
   - Azure CLI logged in (`az login`)
   - Google Cloud SDK with project access
3. **Cloud Provider Accounts**: Active accounts with billing enabled

### AWS Deployment

```bash
cd aws/
terraform init
terraform plan
terraform apply
```

**Outputs**:
- `public_ip`: EC2 instance public IP
- `application_url`: Direct URL to transactions endpoint

### Azure Deployment

```bash
cd azure/
# Copy and configure the variables file
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars and set your actual Azure subscription ID

terraform init
terraform plan
terraform apply
```

**Alternative using environment variable**:
```bash
cd azure/
export TF_VAR_subscription_id="your-azure-subscription-id"
terraform init
terraform plan
terraform apply
```

**Outputs**:
- `public_ip`: Azure VM public IP
- `application_url`: Direct URL to metrics endpoint

**Note**: VM password is randomly generated and stored in Terraform state.

### GCP Deployment

```bash
cd gcp/
# Copy and configure the variables file
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars and set your actual GCP project ID

terraform init
terraform plan
terraform apply
```

**Alternative using environment variable**:
```bash
cd gcp/
export TF_VAR_project_id="your-gcp-project-id"
terraform init
terraform plan
terraform apply
```

**Outputs**:
- `instance_public_ip`: Compute Engine instance public IP
- `application_url`: Direct URL to customers endpoint

### GCP Inventory Service Deployment

```bash
cd gcp/
# Copy and configure the variables file (if not already done)
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars and set your actual GCP project ID

# Enable required APIs (if not already enabled)
gcloud services enable compute.googleapis.com
gcloud services enable servicenetworking.googleapis.com

terraform init
terraform plan -target=google_compute_network.inventory_vpc  # Plan VPC first
terraform apply -target=google_compute_network.inventory_vpc  # Create VPC first
terraform plan  # Plan remaining resources
terraform apply
```

**Outputs**:
- `inventory_vm_private_ip`: Private IP of the inventory VM (no external access)
- `inventory_psc_endpoint_ip`: PSC endpoint IP accessible from default VPC
- `inventory_service_url`: Direct URL to inventory service via PSC
- `inventory_vpc_name`: Name of the dedicated inventory VPC
- `inventory_subnet_cidr`: CIDR range of the inventory subnet

## Testing the Services

### Using curl

**Test AWS Accounting Service**:
```bash
# List transactions
curl http://<aws-ip>:8080/transactions

# Add transaction
curl -X POST http://<aws-ip>:8080/transactions \
  -H "Content-Type: application/json" \
  -d '{"item":"Test Item","price":99.99,"date":"2025-01-15"}'
```

**Test Azure Analytics Service**:
```bash
# Get metrics
curl http://<azure-ip>:8080/metrics

# Record metric
curl -X POST http://<azure-ip>:8080/metrics \
  -H "Content-Type: application/json" \
  -d '{"transactionType":"checkout","durationMs":150,"success":true}'
```

**Test GCP CRM Service**:
```bash
# List customers
curl http://<gcp-ip>:8080/customers

# Add customer
curl -X POST http://<gcp-ip>:8080/customers \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","surname":"Johnson"}'
```

**Test GCP Inventory Service** (via PSC from default VPC):
```bash
# Note: This service is only accessible via PSC endpoint from default VPC
# Get PSC endpoint IP from terraform output
INVENTORY_PSC_IP=$(terraform output -raw inventory_psc_endpoint_ip)

# List all inventory
curl http://$INVENTORY_PSC_IP:8080/inventory

# Get specific product inventory
curl http://$INVENTORY_PSC_IP:8080/inventory/OLJCESPC7Z

# Reserve stock
curl -X POST http://$INVENTORY_PSC_IP:8080/inventory/OLJCESPC7Z/reserve \
  -H "Content-Type: application/json" \
  -d '{"quantity":2}'

# Release reserved stock
curl -X POST http://$INVENTORY_PSC_IP:8080/inventory/OLJCESPC7Z/release \
  -H "Content-Type: application/json" \
  -d '{"quantity":1}'

# Update stock levels (admin operation)
curl -X PUT http://$INVENTORY_PSC_IP:8080/inventory/OLJCESPC7Z \
  -H "Content-Type: application/json" \
  -d '{"stockLevel":50}'
```

## Cost Considerations

- **AWS**: t2.micro instances are free-tier eligible for 12 months
- **Azure**: Standard_B1s offers burstable performance, pay-per-use
- **GCP**: e2-micro instances have always-free tier allowances

## Security Notes

- All services accept traffic from any IP (0.0.0.0/0) for demonstration purposes
- In production, restrict source IP ranges to specific networks
- Consider implementing authentication and HTTPS termination
- VM credentials are managed differently per cloud provider

## Cleanup

To avoid ongoing charges, destroy resources when done:

```bash
# In each service directory
terraform destroy
```

## Troubleshooting

### Common Issues

1. **Service not responding**: Wait 2-3 minutes after deployment for application startup
2. **Connection refused**: Check security group/firewall rules
3. **404 errors**: Verify the service endpoints match the API contract
4. **GCP project errors**: Ensure project ID is correctly set and billing is enabled

### Logs Access

- **AWS**: Use EC2 console or SSH to check application logs
- **Azure**: Use Azure portal serial console or SSH with generated password
- **GCP**: Use GCP console serial port or SSH through browser

## Integration Example

## Complete Ecommerce Workflow

These four services create a complete ecommerce business workflow:

1. **Customer Management** (GCP CRM): Register and manage customer data
2. **Inventory Management** (GCP Inventory): Check stock availability and reserve products  
3. **Transaction Processing** (AWS Accounting): Record financial transactions
4. **Performance Analytics** (Azure Analytics): Track system performance and metrics

## Service Integration Patterns

These services can be integrated into a larger microservices architecture where:
- Accounting service tracks financial transactions
- Analytics service monitors transaction performance
- CRM service manages customer data

Example integration flow:
1. Customer places order (CRM service)
2. Transaction processed (Accounting service)
3. Performance metrics recorded (Analytics service) 