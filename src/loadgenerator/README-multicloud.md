# Multicloud Load Generator

This enhanced load generator can test both the original Online Boutique application and your deployed multicloud services across AWS, Azure, and GCP.

## What's New

The load generator has been updated to support testing 3 additional services:

1. **AWS Accounting Service** - Financial transaction management
2. **Azure Analytics Service** - Performance metrics collection  
3. **GCP CRM Service** - Customer relationship management

## REST API Testing

The load generator follows a **POST then GET** pattern for each service:

### AWS Accounting Service
- **POST** `/transactions` - Creates a new transaction with random data
- **GET** `/transactions` - Retrieves all transactions

### Azure Analytics Service  
- **POST** `/metrics` - Records a new performance metric
- **GET** `/metrics` - Retrieves metrics summary and data

### GCP CRM Service
- **POST** `/customers` - Adds a new customer
- **GET** `/customers` - Retrieves all customers

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AWS_ACCOUNTING_URL` | Full URL to AWS accounting service | None | Yes (for multicloud) |
| `AZURE_ANALYTICS_URL` | Full URL to Azure analytics service | None | Yes (for multicloud) |
| `GCP_CRM_URL` | Full URL to GCP CRM service | None | Yes (for multicloud) |
| `ENABLE_MULTICLOUD_TESTS` | Enable multicloud service testing | `true` | No |
| `USERS` | Number of concurrent users | `10` | No |
| `RATE` | Users spawned per second | `1` | No |
| `USER_CLASS` | Locust user class to run | `CombinedUser` | No |
| `FRONTEND_ADDR` | Boutique frontend address (legacy) | None | No |

### User Classes

| Class | Description |
|-------|-------------|
| `WebsiteUser` | Tests only the original boutique application |
| `MulticloudUser` | Tests only the multicloud services |
| `CombinedUser` | Tests both boutique and multicloud services |

## Usage Examples

### 1. Quick Start with Example Script

1. Get your service IP addresses from terraform outputs:
   ```bash
   # In each terraform directory (aws/, azure/, gcp/)
   terraform output
   ```

2. Update the IP addresses in `multicloud-example.sh`:
   ```bash
   AWS_ACCOUNTING_IP="your-aws-ip"
   AZURE_ANALYTICS_IP="your-azure-ip"  
   GCP_CRM_IP="your-gcp-ip"
   ```

3. Run the load test:
   ```bash
   ./multicloud-example.sh
   ```

### 2. Docker Usage

Build and run with Docker:
```bash
# Build the image
docker build -t multicloud-loadgen .

# Run multicloud tests only
docker run --rm \
  -e AWS_ACCOUNTING_URL="http://your-aws-ip:8080" \
  -e AZURE_ANALYTICS_URL="http://your-azure-ip:8080" \
  -e GCP_CRM_URL="http://your-gcp-ip:8080" \
  -e USERS=20 \
  -e RATE=5 \
  -e USER_CLASS=MulticloudUser \
  multicloud-loadgen
```

### 3. Local Python Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AWS_ACCOUNTING_URL="http://your-aws-ip:8080"
export AZURE_ANALYTICS_URL="http://your-azure-ip:8080" 
export GCP_CRM_URL="http://your-gcp-ip:8080"
export GCP_INVENTORY_URL="http://your-psc-ip:8080"
export USERS=20
export RATE=5

# Run load test
locust --headless -u $USERS -r $RATE --user-classes MulticloudUser
```

### 4. Kubernetes Deployment

Update your loadgenerator deployment with the new environment variables:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loadgenerator
spec:
  template:
    spec:
      containers:
      - name: main
        image: your-registry/loadgenerator:latest
        env:
        - name: AWS_ACCOUNTING_URL
          value: "http://your-aws-ip:8080"
        - name: AZURE_ANALYTICS_URL  
          value: "http://your-azure-ip:8080"
        - name: GCP_CRM_URL
          value: "http://your-gcp-ip:8080"
        - name: GCP_INVENTORY_URL
          value: "http://your-psc-ip:8080"
        - name: ENABLE_MULTICLOUD_TESTS
          value: "true"
        - name: USER_CLASS
          value: "MulticloudUser"
        - name: USERS
          value: "20"
        - name: RATE
          value: "5"
```

## Testing Modes

### Multicloud Only
Tests only the 3 multicloud services:
```bash
export USER_CLASS=MulticloudUser
export ENABLE_MULTICLOUD_TESTS=true
# Don't set FRONTEND_ADDR
```

### Boutique Only  
Tests only the original boutique application:
```bash
export USER_CLASS=WebsiteUser
export ENABLE_MULTICLOUD_TESTS=false
export FRONTEND_ADDR="your-boutique-url"
```

### Combined Testing
Tests both boutique and multicloud services:
```bash
export USER_CLASS=CombinedUser
export ENABLE_MULTICLOUD_TESTS=true
export FRONTEND_ADDR="your-boutique-url"
# Also set multicloud URLs
```

## Understanding Results

The load test will show statistics for each operation:

```
Name                    # reqs    # fails  |   Avg     Min     Max  Median  |   req/s failures/s
AWS-POST-transaction       45       0(0%)  |   156      89     289     150  |    2.1     0.0
AWS-GET-transactions       45       0(0%)  |    98      67     187      95  |    2.1     0.0
Azure-POST-metric          47       0(0%)  |   134      76     245     125  |    2.2     0.0
Azure-GET-metrics          47       0(0%)  |    89      54     156      86  |    2.2     0.0
GCP-POST-customer          46       0(0%)  |   167      92     298     155  |    2.1     0.0
GCP-GET-customers          46       0(0%)  |   102      71     189      98  |    2.1     0.0
```

## Sample Data Generated

The load generator creates realistic test data:

- **Transactions**: Random items, prices ($10-999), recent dates
- **Metrics**: Various transaction types, duration 50-5000ms, success/failure
- **Customers**: Random first/last name combinations

## Troubleshooting

### Common Issues

1. **Connection refused**: Check if your services are running and accessible
2. **404 errors**: Verify the service URLs and endpoints are correct
3. **Timeout errors**: Services might be starting up, wait 2-3 minutes after deployment

### Debugging

Enable verbose logging:
```bash
locust --loglevel DEBUG --headless -u 1 -r 1 --user-classes MulticloudUser
```

### Testing Individual Services

Test one service at a time by setting only one URL:
```bash
# Test only AWS
export AWS_ACCOUNTING_URL="http://your-aws-ip:8080"
unset AZURE_ANALYTICS_URL GCP_CRM_URL
```

## Backward Compatibility

The load generator maintains full backward compatibility with the original boutique testing. Existing deployments will continue to work without changes.

## Next Steps

- Monitor your cloud provider dashboards during load tests
- Adjust USERS and RATE based on your service capacity
- Use the results to optimize your service performance
- Scale your services based on load test findings 