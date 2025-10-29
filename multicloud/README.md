# Multicloud Infrastructure Documentation

This folder contains Terraform configurations that deploy microservices across Azure and Google Cloud Platform, demonstrating various deployment patterns including VMs, Cloud Run, and advanced networking configurations.

## Architecture Overview

The multicloud setup demonstrates modern microservices deployment patterns with various networking and compute options:

### Azure Services
- **Analytics Service** (Performance metrics) - VM with Public IP

### GCP Services
- **CRM Service** (Customer relationship management) - VM with Public IP
- **Inventory Service** (Stock management) - VM with Private IP only
- **Furniture Service** (Furniture catalog) - VM with Public IP
- **Food Service** (Food catalog) - Cloud Run with Direct VPC Egress
- **Accounting Service** (Financial transactions) - Cloud Run with VPC Connector

### Network Architecture

**Service Isolation**: Each GCP service in its own dedicated VPC for security
- `crm-vpc` (10.2.0.0/24) - CRM service
- `inventory-vpc` (10.1.0.0/24) - Inventory service  
- `furniture-vpc` (10.3.0.0/24) - Furniture service
- `online-boutique-vpc` - Online Boutique GKE cluster

**Advanced Networking Patterns**:
- **Private Service Connect (PSC)**: Secure private connection to inventory service
- **Direct VPC Egress**: Food service (Cloud Run) directly connected to inventory VPC
- **VPC Connector**: Accounting service (Cloud Run) connected to CRM VPC via Serverless VPC Access
- **Firewall Rules**: Granular control for service-to-service communication

**Cloud Run Networking Comparison**:
| Pattern | Use Case | Throughput | IP Range |
|---------|----------|------------|----------|
| Direct VPC Egress | Frequent communication | No limits | From target subnet |
| VPC Connector | Occasional access | 200-300 Mbps | Dedicated /28 |

All VM services run Node.js applications on port 8080 with RESTful APIs.

## Services Overview

### 1. Azure Analytics Service (`azure/analytics.tf`)

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

### 2. GCP CRM Service (`gcp/crm.tf`)

**Purpose**: Manages customer relationship data  
**Cloud Provider**: Google Cloud Platform  
**Instance**: e2-micro (Compute Engine VM)  
**Region**: us-central1  
**Network**: Public IP with external access

#### Infrastructure Components
- Dedicated VPC network (crm-vpc) with 10.2.0.0/24 subnet
- Compute Engine instance with Debian 11 and external IP
- Firewall rule allowing HTTP traffic on port 8080
- Automated Node.js application deployment via startup script
- Cloud NAT for outbound internet access

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

### 3. GCP Inventory Service (`gcp/inventory.tf`)

**Purpose**: Manages product stock levels, reservations, and availability  
**Cloud Provider**: Google Cloud Platform  
**Instance**: e2-micro (Compute Engine VM)  
**Region**: us-central1  
**Network**: Private IP only (no external access)

#### Infrastructure Components
- Dedicated VPC network (inventory-vpc) with 10.1.0.0/24 subnet
- VM with private IP only (no external IP access)
- Cloud NAT for outbound internet access (package installation)
- Private Service Connect (PSC) for secure connectivity
- Firewall rules for internal and PSC traffic

#### Security Features
- **Private IP only**: VM has no external IP address
- **Network isolation**: Separate VPC for inventory data
- **PSC connectivity**: Secure private connection from other VPCs
- **Controlled access**: Firewall rules restrict traffic to necessary ports

#### REST API Contract

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

### 4. GCP Furniture Service (`gcp/furniture.tf`)

**Purpose**: Manages furniture product catalog  
**Cloud Provider**: Google Cloud Platform  
**Instance**: e2-micro (Compute Engine VM)  
**Region**: europe-west1  
**Network**: Public IP with external access

#### Infrastructure Components
- Dedicated VPC network (furniture-vpc) with 10.3.0.0/24 subnet
- Compute Engine instance with Debian 11 and external IP
- Firewall rule allowing HTTP traffic on port 8080
- Inline Node.js application deployment via startup script
- Cloud NAT for outbound internet access

#### REST API Contract

**Base URL**: `http://<public-ip>:8080`

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/furniture` | List all furniture items | None | Array of furniture objects |
| GET | `/furniture/:id` | Get specific furniture item | None | Furniture object |
| POST | `/furniture` | Add new furniture item | `{"name": "string", "category": "string", "price": number}` | Created furniture object |
| PUT | `/furniture/:id` | Update furniture item | `{"name": "string", "category": "string", "price": number}` | Updated furniture object |
| DELETE | `/furniture/:id` | Delete furniture item | None | Success message |

**Sample Data**:
```json
[
  { "id": 1, "name": "Oak Desk", "category": "Office", "price": 299.99 },
  { "id": 2, "name": "Leather Sofa", "category": "Living Room", "price": 899.99 }
]
```

### 5. GCP Food Service (`gcp/food.tf` + `gcp/food-service/`)

**Purpose**: Manages food product catalog with inventory integration  
**Cloud Provider**: Google Cloud Platform  
**Platform**: Cloud Run (serverless containers)  
**Region**: europe-west1  
**Network**: Direct VPC Egress to inventory-vpc

#### Infrastructure Components
- Cloud Run service with containerized Node.js application
- Artifact Registry for Docker image storage
- Cloud Build for automated CI/CD pipeline
- Direct VPC Egress to inventory-vpc (10.1.0.0/24)
- Firewall rules allowing Cloud Run to inventory service

#### Networking Features
- **Direct VPC Egress**: Cloud Run directly connected to inventory VPC subnet
- **Private Ranges Only**: Egress traffic only to private IP ranges
- **No Throughput Limits**: Full network performance
- **Inventory Integration**: Calls inventory service at every request

#### REST API Contract

**Base URL**: `https://<cloud-run-url>`

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/health` | Health check endpoint | None | Service status |
| GET | `/food` | List food items with inventory check | None | Food items + inventory data |
| GET | `/food/:id` | Get specific food item | None | Food object |
| POST | `/food` | Add new food item | `{"name": "string", "category": "string", "price": number, "available": boolean}` | Created food object |
| PUT | `/food/:id` | Update food item | `{"name": "string", "category": "string", "price": number, "available": boolean}` | Updated food object |
| DELETE | `/food/:id` | Delete food item | None | Success message |

**Sample Response** (GET `/food`):
```json
{
  "foodItems": [
    { "id": 1, "name": "Pizza Margherita", "category": "Italian", "price": 12.99 }
  ],
  "inventoryCheck": {
    "checked": true,
    "inventoryItems": [
      { "productId": "OLJCESPC7Z", "stockLevel": 45, "available": 42 }
    ],
    "timestamp": "2025-10-29T..."
  }
}
```

### 6. GCP Accounting Service (`gcp/accounting.tf` + `gcp/accounting-service/`)

**Purpose**: Manages financial transactions with CRM integration  
**Cloud Provider**: Google Cloud Platform  
**Platform**: Cloud Run (serverless containers)  
**Region**: us-central1  
**Network**: VPC Connector to crm-vpc

#### Infrastructure Components
- Cloud Run service with containerized Node.js application
- Artifact Registry for Docker image storage
- Cloud Build for automated CI/CD pipeline
- VPC Connector (10.2.1.0/28) for CRM access
- Firewall rules allowing VPC Connector to CRM service

#### Networking Features
- **VPC Connector**: Serverless VPC Access connector for occasional CRM calls
- **Private Ranges Only**: Egress traffic only to private IP ranges
- **Throughput Limits**: Configurable 200-300 Mbps
- **CRM Integration**: Calls CRM service to retrieve customer data

#### REST API Contract

**Base URL**: `https://<cloud-run-url>`

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/health` | Health check endpoint | None | Service status |
| GET | `/transactions` | List transactions with CRM data | None | Transactions + CRM customer list |
| GET | `/transactions/:id` | Get specific transaction | None | Transaction object |
| POST | `/transactions` | Add new transaction | `{"item": "string", "price": number, "date": "YYYY-MM-DD", "customer": "string"}` | Created transaction object |
| PUT | `/transactions/:id` | Update transaction | `{"item": "string", "price": number, "date": "YYYY-MM-DD", "customer": "string"}` | Updated transaction object |
| DELETE | `/transactions/:id` | Delete transaction | None | Success message |

**Sample Response** (GET `/transactions`):
```json
{
  "transactions": [
    { "id": 1, "item": "Office Supplies", "price": 75.50, "date": "2025-07-20" }
  ],
  "crmIntegration": {
    "connected": true,
    "customers": [
      { "name": "mark86@example.net", "surname": "Customer" }
    ],
    "timestamp": "2025-10-29T..."
  }
}
```

## Deployment Instructions

### Prerequisites

1. **Terraform**: Install Terraform >= 1.0
2. **Cloud CLI Tools**: 
   - Azure CLI logged in (`az login`)
   - Google Cloud SDK with project access (`gcloud auth login`)
   - Docker for building Cloud Run images
3. **Cloud Provider Accounts**: Active accounts with billing enabled
4. **GCP APIs**: Enable required APIs:
```bash
   gcloud services enable compute.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable vpcaccess.googleapis.com
   gcloud services enable servicenetworking.googleapis.com
   ```

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

**File Structure:**
```
gcp/
├── main.tf             # Shared Terraform, provider, and variable configs
├── crm.tf              # CRM service (VM with public IP)
├── inventory.tf        # Inventory service (VM with private IP + PSC)
├── furniture.tf        # Furniture service (VM with public IP)
├── food.tf             # Food service (Cloud Run with Direct VPC Egress)
├── accounting.tf       # Accounting service (Cloud Run with VPC Connector)
├── food-service/       # Food service application code
├── accounting-service/ # Accounting service application code
└── terraform.tfvars    # Your project configuration
```

#### Step 1: Deploy VM-based services (CRM, Inventory, Furniture)

```bash
cd gcp/

# Copy and configure the variables file
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars and set:
#   - project_id: Your GCP project ID
#   - region: Your preferred region (default: us-central1)
#   - zone: Your preferred zone (default: us-central1-a)

# Deploy VM services
terraform init
terraform plan
terraform apply
```

**VM Services Outputs**:
- `crm_vm_public_ip`: CRM service public IP
- `crm_vm_private_ip`: CRM service private IP
- `inventory_vm_private_ip`: Inventory VM private IP (no external access)
- `inventory_psc_endpoint_ip`: PSC endpoint to access inventory
- `furniture_vm_public_ip`: Furniture service public IP

#### Step 2: Build and deploy Food Service (Cloud Run)

```bash
cd gcp/food-service/

# Build and push Docker image
./build.sh

# Or manually:
gcloud builds submit --config=cloudbuild.yaml \
  --project=your-project-id

# Deploy with Terraform (already configured in food.tf)
cd ..
terraform apply
```

**Food Service Outputs**:
- `food_service_url`: Cloud Run service URL
- `food_vpc_config`: VPC egress configuration details

#### Step 3: Build and deploy Accounting Service (Cloud Run)

```bash
cd gcp/accounting-service/

# Build and push Docker image
./build.sh

# Or manually:
gcloud builds submit --config=cloudbuild.yaml \
  --project=your-project-id

# Deploy with Terraform (already configured in accounting.tf)
cd ..
terraform apply
```

**Accounting Service Outputs**:
- `accounting_service_url`: Cloud Run service URL
- `accounting_vpc_connector`: VPC Connector configuration

#### Alternative: Deploy All Services at Once

```bash
cd gcp/

# Build both Cloud Run services first
cd food-service && ./build.sh && cd ..
cd accounting-service && ./build.sh && cd ..

# Deploy everything with Terraform
terraform init
terraform plan
terraform apply
```

## Testing the Services

### Using curl

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

**Test GCP Inventory Service** (via PSC):
```bash
# Get PSC endpoint IP from terraform output
INVENTORY_PSC_IP=$(terraform output -raw inventory_psc_endpoint_ip)

# Health check
curl http://$INVENTORY_PSC_IP:8080/health

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

# Update stock levels
curl -X PUT http://$INVENTORY_PSC_IP:8080/inventory/OLJCESPC7Z \
  -H "Content-Type: application/json" \
  -d '{"stockLevel":50}'
```

**Test GCP Furniture Service**:
```bash
# Get furniture service IP
FURNITURE_IP=$(terraform output -raw furniture_vm_public_ip)

# List all furniture
curl http://$FURNITURE_IP:8080/furniture

# Get specific item
curl http://$FURNITURE_IP:8080/furniture/1

# Add furniture item
curl -X POST http://$FURNITURE_IP:8080/furniture \
  -H "Content-Type: application/json" \
  -d '{"name":"Modern Chair","category":"Office","price":199.99}'

# Update furniture item
curl -X PUT http://$FURNITURE_IP:8080/furniture/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Executive Desk","category":"Office","price":499.99}'

# Delete furniture item
curl -X DELETE http://$FURNITURE_IP:8080/furniture/1
```

**Test GCP Food Service** (Cloud Run with inventory integration):
```bash
# Get food service URL
FOOD_URL=$(terraform output -raw food_service_url)

# Health check
curl $FOOD_URL/health

# List food items (includes inventory check)
curl $FOOD_URL/food

# Get specific food item
curl $FOOD_URL/food/1

# Add food item
curl -X POST $FOOD_URL/food \
  -H "Content-Type: application/json" \
  -d '{"name":"Caesar Salad","category":"Salad","price":8.99,"available":true}'

# Update food item
curl -X PUT $FOOD_URL/food/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Margherita Pizza","category":"Italian","price":14.99,"available":true}'

# Delete food item
curl -X DELETE $FOOD_URL/food/1
```

**Test GCP Accounting Service** (Cloud Run with CRM integration):
```bash
# Get accounting service URL
ACCOUNTING_URL=$(terraform output -raw accounting_service_url)

# Health check
curl $ACCOUNTING_URL/health

# List transactions (includes CRM customer data)
curl $ACCOUNTING_URL/transactions

# Get specific transaction
curl $ACCOUNTING_URL/transactions/1

# Add transaction
curl -X POST $ACCOUNTING_URL/transactions \
  -H "Content-Type: application/json" \
  -d '{"item":"Office Supplies","price":99.99,"date":"2025-10-29","customer":"John Doe"}'

# Update transaction
curl -X PUT $ACCOUNTING_URL/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"item":"Software License","price":299.99,"date":"2025-10-29","customer":"Jane Smith"}'

# Delete transaction
curl -X DELETE $ACCOUNTING_URL/transactions/1
```

## Cost Considerations

### Azure
- **Standard_B1s**: Burstable performance, pay-per-use (~$10-15/month)
- **Public IP**: Small charge for static IP allocation

### GCP Compute Engine (VMs)
- **e2-micro**: Always-free tier eligible (1 per month per region)
- **CRM, Inventory, Furniture**: ~$5-8/month each if not in free tier
- **Cloud NAT**: ~$0.045/hour + data processing charges

### GCP Cloud Run (Serverless)
- **Food & Accounting Services**: Pay-per-request pricing
  - First 2 million requests free per month
  - $0.40 per million requests after that
  - CPU/Memory only charged during request processing
  - Minimal cost for low traffic (~$1-5/month)

### GCP Networking
- **VPC Connector**: ~$0.035/hour (~$25/month) + data processing
- **Direct VPC Egress**: More cost-effective, no connector charges
- **Private Service Connect**: $0.01/GB processed
- **Inter-region data transfer**: $0.01-0.12/GB depending on regions

### Cost Optimization Tips
1. Use Direct VPC Egress instead of VPC Connector when possible
2. Set Cloud Run min instances to 0 for development
3. Use e2-micro instances in free tier
4. Monitor Cloud NAT data processing costs
5. Consider regional deployment to minimize data transfer

## Security Notes

- **Public Services**: Accept traffic from 0.0.0.0/0 for demonstration
- **Private Services**: Inventory VM has no external IP, only PSC access
- **Network Isolation**: Each service in dedicated VPC
- **Firewall Rules**: Granular control per service
- **Production Recommendations**:
  - Restrict source IP ranges to known networks
  - Implement authentication (Cloud IAM, API keys)
  - Enable HTTPS termination (Cloud Load Balancer)
  - Use Secret Manager for sensitive data
  - Enable VPC Flow Logs for audit trails

## Cleanup

To avoid ongoing charges, destroy resources when done:

```bash
# In each service directory
terraform destroy
```

## Troubleshooting

### Common Issues

1. **Service not responding**: 
   - Wait 2-3 minutes after deployment for VM application startup
   - Cloud Run services start instantly but may have cold starts
   - Check firewall rules and VPC configurations

2. **Connection refused**: 
   - Verify firewall rules allow traffic on port 8080
   - Check if VM is running: `gcloud compute instances list`
   - For Cloud Run, ensure service is deployed: `gcloud run services list`

3. **404 errors**: 
   - Verify the service endpoints match the API contract
   - Check application logs for startup errors

4. **Cloud Run to VM connection failures**:
   - Verify VPC Connector or Direct VPC Egress is configured
   - Check firewall rules allow traffic from Cloud Run subnet
   - Ensure target VM has correct internal IP

5. **GCP project errors**: 
   - Ensure project ID is correctly set and billing is enabled
   - Verify all required APIs are enabled (see Prerequisites)

### Logs Access

- **Azure VMs**: Use Azure portal serial console or SSH with generated password
- **GCP VMs**: 
  ```bash
  gcloud compute ssh <instance-name> --zone=<zone>
  # Check logs: sudo journalctl -u app.service -f
  # Or: sudo cat /var/log/startup-script.log
  ```
- **GCP Cloud Run**:
  ```bash
  gcloud run services logs read <service-name> --region=<region>
  # Or use Cloud Console Logs Explorer
  ```

### Debugging Network Issues

**Test VPC connectivity:**
```bash
# From GKE pod or Cloud Shell in same VPC
curl http://10.1.0.2:8080/health  # Inventory service
curl http://10.2.0.2:8080/health  # CRM service
curl http://10.3.0.2:8080/health  # Furniture service
```

**Check firewall rules:**
```bash
gcloud compute firewall-rules list --filter="network:inventory-vpc"
```

**Verify VPC Connector:**
```bash
gcloud compute networks vpc-access connectors list --region=us-central1
```

## Complete Ecommerce Workflow

These services create a complete multicloud ecommerce platform:

### Service Architecture

```
┌─────────────────┐
│ Online Boutique │ (GKE Kubernetes)
│   Checkout      │
└────────┬────────┘
         │
    ┌────┴────┬───────────┬──────────────┐
    │         │           │              │
    ▼         ▼           ▼              ▼
┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│  Food  │ │Accounting│ │Furniture │ │Analytics │
│Service │ │ Service │ │ Service  │ │ Service  │
│(Cloud  │ │(Cloud   │ │  (VM)    │ │  (Azure) │
│ Run)   │ │  Run)   │ │          │ │          │
└───┬────┘ └────┬─────┘ └──────────┘ └──────────┘
    │           │
    │ Direct    │ VPC
    │ VPC Egress│ Connector
    │           │
    ▼           ▼
┌──────────┐ ┌─────────┐
│Inventory │ │   CRM   │
│ Service  │ │ Service │
│(Private) │ │  (VM)   │
└──────────┘ └─────────┘
```

### Integration Flow

1. **Customer browses catalog** → Food/Furniture services provide product data
2. **Check inventory** → Food service calls Inventory service (Direct VPC Egress)
3. **Customer checkout** → Checkout service orchestrates the flow
4. **Record transaction** → Accounting service saves transaction + fetches CRM data (VPC Connector)
5. **Track metrics** → Analytics service records performance data
6. **Update inventory** → Inventory service reserves/releases stock

### Key Integration Points

| Service | Calls | Via | Purpose |
|---------|-------|-----|---------|
| Checkout | Food Service | Public HTTPS | Get food catalog |
| Checkout | Accounting Service | Public HTTPS | Record transactions |
| Food Service | Inventory Service | Direct VPC Egress | Check stock levels |
| Accounting Service | CRM Service | VPC Connector | Get customer data |

### Example: Complete Order Flow

```bash
# 1. Customer checks food menu
curl https://food-service-url/food
# Response includes inventory check from Inventory service

# 2. Customer places order via checkout
# Checkout service internally calls:
#   - Food service (validate items)
#   - Accounting service (create transaction)

# 3. Accounting service records transaction
curl https://accounting-service-url/transactions
# Response includes CRM customer data

# 4. Analytics tracks the performance
curl http://azure-analytics-ip:8080/metrics
# Shows transaction performance metrics
```

## Benefits of This Architecture

1. **Multi-cloud resilience**: Services distributed across providers
2. **Network security**: Private services with controlled access
3. **Cost optimization**: Serverless for variable workloads, VMs for consistent loads
4. **Scalability**: Cloud Run auto-scales, VMs can be managed instance groups
5. **Service isolation**: Each service in dedicated VPC/network
6. **Modern patterns**: Demonstrates both VM and serverless deployments 