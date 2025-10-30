# Terraform Configuration Summary

## Overview
This document summarizes the Terraform configuration for the **network-obs-demo** GCP project. All infrastructure resources are managed in a single project with Terraform state stored remotely in Google Cloud Storage.

## Project Configuration

### Single Project Setup
All resources are deployed in the **network-obs-demo** project. The configuration uses variables consistently to avoid hardcoding project IDs.

### Remote State Storage
Terraform state is stored in Google Cloud Storage for:
- **Collaboration**: Multiple team members can work with the same state
- **Security**: State is not stored in Git repository
- **Versioning**: GCS bucket has versioning enabled for state recovery
- **Locking**: Automatic state locking prevents concurrent modifications

**GCS Bucket**: `gs://network-obs-demo-terraform-state/terraform/state/`

## Infrastructure Components

### CRM Service (asia-east1)
- **VPC Network**: `crm-vpc` (global)
- **Subnet**: `crm-subnet` in asia-east1 with IP range 10.3.0.0/24
- **VM Instance**: `crm-vm` in asia-east1-a
- **Firewall Rules**: 
  - `crm-allow-http-internal` - allows port 8080 from internal networks
  - `allow-accounting-connector-to-crm` - allows VPC connector access
- **VPC Peerings**:
  - `crm-to-ob` - CRM VPC to Online Boutique VPC
  - `ob-to-crm` - Online Boutique VPC to CRM VPC
  - `ob-to-remote` - Online Boutique to remote project (cci-dev-playground)

### Accounting Service (us-central1)
- **VPC Access Connector**: `accounting-connector` in us-central1
  - IP range: 10.3.1.0/28
  - Throughput: 200-1000 Mbps
  - Connects Cloud Run to CRM VPC

### Inventory Service (europe-west1)
- **VPC Network**: `inventory-vpc` (global)
- **Subnets**:
  - `inventory-subnet` - main subnet (10.20.0.0/24)
  - `inventory-psc-subnet` - Private Service Connect subnet (10.20.1.0/24)
- **VM Instance**: `inventory-service-vm` in europe-west1-b
- **Instance Group**: `inventory-instance-group`
- **Load Balancing**:
  - Backend service with health checks
  - Internal forwarding rule
- **Private Service Connect**:
  - Service attachment for cross-VPC access
  - PSC endpoint in europe-west1
  - Reserved IP address
- **Firewall Rules**:
  - `inventory-allow-internal` - internal traffic
  - `inventory-allow-psc` - PSC traffic

### Food Service (europe-west1)
- **Cloud Run Service**: API service connecting to inventory
- **Artifact Registry**: Docker repository for food service
- **Firewall Rule**: `allow-cloud-run-to-inventory` - allows Cloud Run to access inventory VM

## Configuration Files

### Core Files
- **main.tf**: Provider configuration, variables, and backend configuration
- **terraform.tfvars**: Project-specific variable values (not in Git)
- **terraform.tfvars.example**: Template for variable configuration

### Service Files
- **crm.tf**: CRM service infrastructure and VPC peerings
- **accounting.tf**: Accounting Cloud Run service and VPC connector
- **inventory.tf**: Inventory service with PSC configuration
- **food.tf**: Food service Cloud Run configuration

## Variables

### Required Variables
All configured in `terraform.tfvars`:

```hcl
project_id            = "network-obs-demo"
gcp_project_id        = "network-obs-demo"
region                = "us-central1"
zone                  = "us-central1-a"
ob_network_name       = "online-boutique-vpc"
ob_subnet_name        = "subnet1-us-central1"
peering_project_id    = "cci-dev-playground"
peering_vpc_network   = "location-verification"
inventory_service_url = "http://10.1.0.2:8080"
crm_service_url       = "http://10.3.0.2:8080"
```

**Important**: Never commit `terraform.tfvars` to Git as it may contain sensitive information.

## Terraform State Management

### Backend Configuration
```hcl
terraform {
  backend "gcs" {
    bucket = "network-obs-demo-terraform-state"
    prefix = "terraform/state"
  }
}
```

### State Operations

**Initialize and migrate state**:
```bash
terraform init
```

**View current state**:
```bash
terraform state list
```

**Pull remote state**:
```bash
terraform state pull
```

**Import existing resources**:
```bash
terraform import <resource_type>.<resource_name> <resource_id>
```

## Working with Terraform

### Standard Workflow

1. **Initialize** (first time or after backend changes):
   ```bash
   terraform init
   ```

2. **Plan changes**:
   ```bash
   terraform plan
   ```

3. **Apply changes**:
   ```bash
   terraform apply
   ```

4. **Destroy resources** (if needed):
   ```bash
   terraform destroy
   ```

### Targeting Specific Resources

Create or update specific resources:
```bash
terraform apply -target=google_cloud_run_v2_service.accounting_api_service
```

### Best Practices

1. **Always run `terraform plan`** before `apply` to review changes
2. **Use descriptive commit messages** when changing Terraform configurations
3. **Never commit state files** - they're in GCS and excluded via .gitignore
4. **Use variables** instead of hardcoding values
5. **Test changes in isolation** using `-target` when appropriate
6. **Keep terraform.tfvars up to date** but never commit it to Git

## Current State

### Resources Managed by Terraform
All infrastructure in the network-obs-demo project is now tracked in Terraform state:
- ✅ VPC networks and subnets
- ✅ VM instances and instance groups
- ✅ Firewall rules
- ✅ VPC peering connections
- ✅ Load balancers and health checks
- ✅ Private Service Connect resources
- ✅ VPC Access Connectors

### Resources to be Created
When you run `terraform apply`, these will be created:
- Artifact Registry repositories
- Cloud Run services for accounting and food APIs
- Cloud Run IAM bindings for public access
- Project service API enablements

### Known State Differences
Some VM instances show as needing replacement due to metadata format differences between manual creation and Terraform definitions. These are cosmetic differences and the VMs function correctly. You can choose to:
- **Option A**: Leave them as-is (recommended) - they work fine
- **Option B**: Allow Terraform to replace them for perfect alignment (causes temporary downtime)

## Migration History

### Recent Changes
1. **Consolidated to single project**: Removed references to secondary project
2. **Removed furniture.tf**: Deleted as it referenced old project infrastructure
3. **Enabled remote state**: Migrated from local state to GCS
4. **Fixed configuration**: Updated subnet names and peering settings to match actual GCP resources
5. **Imported manual resources**: All manually created resources now tracked in Terraform

### CRM Service Migration
The CRM VM was migrated from us-central1 to asia-east1:
- **Old location**: us-central1-a
- **New location**: asia-east1-a
- **IP range preserved**: 10.3.0.0/24
- **VM IP maintained**: 10.3.0.2

## Troubleshooting

### State Locking Issues
If you see "Error acquiring the state lock":
```bash
# View current lock
terraform force-unlock <LOCK_ID>
```

### Backend Initialization
If backend configuration changes:
```bash
terraform init -reconfigure
```

### State Drift
Check for differences between state and actual infrastructure:
```bash
terraform plan -refresh-only
```

## Security Notes

1. **State file contains sensitive data**: Never commit or share terraform.tfstate
2. **GCS bucket access**: Limit access to the state bucket to authorized users only
3. **Service accounts**: Use dedicated service accounts with minimal required permissions
4. **Variables file**: Keep terraform.tfvars secure and out of version control

## Support and Documentation

- Terraform GCP Provider: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- GCS Backend: https://www.terraform.io/docs/language/settings/backends/gcs.html
- Google Cloud Networking: https://cloud.google.com/vpc/docs
