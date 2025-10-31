# Terraform Configuration Reference

## Overview
Quick reference guide for managing Terraform infrastructure in the **network-obs-demo** GCP project.

## Backend Configuration

Terraform state is stored in Google Cloud Storage:

```hcl
terraform {
  backend "gcs" {
    bucket = "network-obs-demo-terraform-state"
    prefix = "terraform/state"
  }
}
```

**Bucket location**: `gs://network-obs-demo-terraform-state/terraform/state/`

## Standard Workflow

```bash
# 1. Initialize (first time or after backend changes)
terraform init

# 2. Plan changes
terraform plan

# 3. Apply changes
terraform apply

# 4. View current state
terraform state list

# 5. Destroy resources (if needed)
terraform destroy
```

## Targeting Specific Resources

```bash
# Apply specific resource
terraform apply -target=google_cloud_run_v2_service.accounting_api_service

# Plan specific resource
terraform plan -target=google_compute_instance.crm_vm
```

## State Management

### View State
```bash
# List all resources
terraform state list

# Show specific resource
terraform state show google_compute_instance.crm_vm

# Pull remote state (for inspection)
terraform state pull
```

### Import Existing Resources
```bash
# Import a resource
terraform import <resource_type>.<resource_name> <resource_id>

# Example: Import a VM
terraform import google_compute_instance.crm_vm projects/network-obs-demo/zones/asia-east1-a/instances/crm-vm
```

### Remove Resources from State
```bash
# Remove resource from state (doesn't delete from GCP)
terraform state rm google_compute_instance.old_vm
```

## Troubleshooting

### State Locking Issues
```bash
# If state is locked, force unlock
terraform force-unlock <LOCK_ID>
```

### Backend Reinitialization
```bash
# Reconfigure backend
terraform init -reconfigure

# Migrate state
terraform init -migrate-state
```

### State Drift Detection
```bash
# Check for drift between state and actual infrastructure
terraform plan -refresh-only

# Update state to match reality
terraform apply -refresh-only
```

## Variables Configuration

Configure in `terraform.tfvars` (never commit to Git):

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

## Best Practices

1. **Always plan before apply**: Review changes with `terraform plan`
2. **Use version control**: Commit Terraform configurations, not state files
3. **Use remote state**: Already configured with GCS backend
4. **Use variables**: Avoid hardcoding values
5. **State file security**: State is in GCS, excluded from Git via .gitignore
6. **Descriptive commits**: Document infrastructure changes clearly
7. **Test in isolation**: Use `-target` for testing specific resources
8. **Regular backups**: GCS bucket has versioning enabled

## Security Considerations

- **State contains sensitive data**: Never commit terraform.tfstate
- **GCS bucket access**: Limit to authorized team members only
- **Variables file**: Keep terraform.tfvars secure and out of Git
- **Service accounts**: Use least-privilege principles
- **State locking**: Automatic with GCS backend

## Common Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `terraform init` | Initialize working directory |
| `terraform plan` | Show execution plan |
| `terraform apply` | Apply changes |
| `terraform destroy` | Destroy all resources |
| `terraform state list` | List resources in state |
| `terraform state show <resource>` | Show resource details |
| `terraform output` | Show output values |
| `terraform fmt` | Format configuration files |
| `terraform validate` | Validate configuration |
| `terraform import <type> <id>` | Import existing resource |

## Resources

- [Terraform GCP Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GCS Backend Documentation](https://www.terraform.io/docs/language/settings/backends/gcs.html)
- [Google Cloud VPC Documentation](https://cloud.google.com/vpc/docs)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)
