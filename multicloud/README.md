# Multicloud Infrastructure Documentation

This folder contains Terraform configurations that deploy mock services across three major cloud providers: AWS, Azure, and Google Cloud Platform. Each service exposes RESTful APIs for different business functions.

## Architecture Overview

The multicloud setup demonstrates how to deploy similar containerized services across different cloud platforms:

- **AWS**: Accounting Service (Financial transactions)
- **Azure**: Analytics Service (Performance metrics) 
- **GCP**: CRM Service (Customer relationship management)

All services are deployed on virtual machines running Ubuntu/Debian with Node.js applications exposed on port 8080.

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

These services can be integrated into a larger microservices architecture where:
- Accounting service tracks financial transactions
- Analytics service monitors transaction performance
- CRM service manages customer data

Example integration flow:
1. Customer places order (CRM service)
2. Transaction processed (Accounting service)
3. Performance metrics recorded (Analytics service) 