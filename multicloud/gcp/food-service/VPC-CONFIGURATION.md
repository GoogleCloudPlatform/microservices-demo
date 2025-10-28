# Food Service VPC Configuration

## Overview

The Food Service on Cloud Run uses **Direct VPC Egress** to securely connect to the Inventory Service running on a private VM in the `inventory-vpc` network.

## Direct VPC Egress vs VPC Connector

| Feature | Direct VPC Egress ✅ | VPC Connector (Legacy) |
|---------|---------------------|------------------------|
| Setup Complexity | Simple | Complex |
| Additional Resources | None | Requires connector instance |
| Cost | Lower | Higher (connector charges) |
| Performance | Better | Good |
| Scalability | Automatic | Limited by connector |

## Network Topology

```
┌─────────────────────────────────────────────────────────┐
│                    Cloud Run (Food Service)              │
│                  europe-west1                            │
│  - Public endpoint for CheckoutService                   │
│  - Direct VPC egress to inventory-vpc                    │
└────────────────┬────────────────────────────────────────┘
                 │ Direct VPC Egress
                 │ (No connector needed!)
                 ▼
┌─────────────────────────────────────────────────────────┐
│              inventory-vpc Network                       │
│              CIDR: 10.20.0.0/24                         │
│                                                          │
│  ┌───────────────────────────────────────┐             │
│  │  inventory-subnet                     │             │
│  │  CIDR: 10.20.0.0/24                  │             │
│  │  region: europe-west1                │             │
│  │                                       │             │
│  │  ┌─────────────────────────────┐    │             │
│  │  │  Inventory Service VM       │    │             │
│  │  │  Tag: inventory-server      │    │             │
│  │  │  Port: 8080                 │    │             │
│  │  │  Internal IP: 10.20.0.X     │    │             │
│  │  └─────────────────────────────┘    │             │
│  └───────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## Terraform Configuration

### 1. Enable Required APIs

```hcl
resource "google_project_service" "food_apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "vpcaccess.googleapis.com",  # Required for VPC access
    "compute.googleapis.com"      # Required for network resources
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}
```

### 2. Reference Existing VPC Resources

```hcl
# Reference to the inventory VPC network
data "google_compute_network" "inventory_vpc" {
  name    = "inventory-vpc"
  project = var.project_id
}

# Reference to the inventory subnet
data "google_compute_subnetwork" "inventory_subnet" {
  name    = "inventory-subnet"
  region  = "europe-west1"
  project = var.project_id
}
```

### 3. Configure Firewall Rules

```hcl
resource "google_compute_firewall" "allow_cloud_run_to_inventory" {
  name    = "allow-cloud-run-to-inventory"
  network = data.google_compute_network.inventory_vpc.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  # Cloud Run instances will use IPs from this subnet
  source_ranges = ["10.20.0.0/24"]
  target_tags   = ["inventory-server"]
  
  description = "Allow Cloud Run food service to access inventory service"
}
```

### 4. Configure Cloud Run with Direct VPC Egress

```hcl
resource "google_cloud_run_v2_service" "food_api_service" {
  # ... other configuration ...

  template {
    containers {
      # ... container configuration ...
    }

    # Direct VPC egress configuration
    vpc_access {
      network_interfaces {
        network    = data.google_compute_network.inventory_vpc.id
        subnetwork = data.google_compute_subnetwork.inventory_subnet.id
      }
      # Route only private IP ranges through VPC (more efficient)
      egress = "PRIVATE_RANGES_ONLY"
    }
  }
}
```

## Egress Settings Comparison

| Setting | Description | Use Case |
|---------|-------------|----------|
| `PRIVATE_RANGES_ONLY` ✅ | Routes only RFC 1918 private IPs through VPC | **Recommended** - More efficient, lower cost |
| `ALL_TRAFFIC` | Routes all traffic through VPC | Use when you need VPC-based controls for all traffic |

## Security Considerations

### Firewall Rules

- **Source**: `10.20.0.0/24` - Cloud Run instances get IPs from this subnet
- **Target**: `inventory-server` tag on the inventory VM
- **Protocol**: TCP
- **Port**: 8080 (inventory service)

### Best Practices

1. ✅ **Use PRIVATE_RANGES_ONLY**: Only route private traffic through VPC
2. ✅ **Minimal Permissions**: Firewall rules target specific tags
3. ✅ **No Public IPs**: Inventory service has no external IP
4. ⚠️ **Public Cloud Run**: Currently allows `allUsers` - restrict in production
5. ✅ **Network Segmentation**: Inventory service in dedicated VPC

## Verification Commands

### Check VPC Configuration

```bash
# Get food service VPC configuration
terraform output food_vpc_config

# Check if Cloud Run service has VPC access
gcloud run services describe food-api-service \
  --region=europe-west1 \
  --format="value(spec.template.spec.containers[0].vpcAccess)"
```

### Verify Firewall Rules

```bash
# List firewall rules for inventory VPC
gcloud compute firewall-rules list \
  --filter="network:inventory-vpc" \
  --format="table(name,sourceRanges,allowed[].map().firewall_rule().list())"

# Check specific rule
gcloud compute firewall-rules describe allow-cloud-run-to-inventory
```

### Test Connectivity

```bash
# From Cloud Run logs, check for successful inventory calls
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=food-api-service \
  AND textPayload=~'inventory'" \
  --limit=50 \
  --format=json
```

### Check Inventory Service

```bash
# Verify inventory VM is running
gcloud compute instances describe inventory-service-vm \
  --zone=europe-west1-b \
  --format="value(name,status,networkInterfaces[0].networkIP)"

# Check if inventory service is listening
gcloud compute ssh inventory-service-vm \
  --zone=europe-west1-b \
  --command="sudo netstat -tlnp | grep 8080"
```

## Troubleshooting

### Problem: Food Service Can't Reach Inventory

**Symptoms:**
- Logs show "Failed to check inventory"
- Timeout errors in Cloud Run logs

**Checks:**
```bash
# 1. Verify VPC access is configured
gcloud run services describe food-api-service \
  --region=europe-west1 \
  --format="get(spec.template.spec.vpcAccess)"

# 2. Check firewall rules
gcloud compute firewall-rules list --filter="name:cloud-run"

# 3. Verify inventory VM is accessible
gcloud compute instances describe inventory-service-vm \
  --zone=europe-west1-b \
  --format="value(status,networkInterfaces[0].networkIP)"

# 4. Check if inventory service is running on VM
gcloud compute ssh inventory-service-vm \
  --zone=europe-west1-b \
  --command="curl -v http://localhost:8080/inventory"
```

### Problem: VPC Access Not Working

**Solution:**
```bash
# Ensure required APIs are enabled
gcloud services enable vpcaccess.googleapis.com compute.googleapis.com

# Re-apply terraform
cd multicloud/gcp
terraform plan
terraform apply
```

### Problem: Wrong Subnet Configuration

**Fix:**
```bash
# Verify the inventory subnet exists and has correct CIDR
gcloud compute networks subnets describe inventory-subnet \
  --region=europe-west1 \
  --format="value(name,ipCidrRange)"

# If subnet doesn't exist, check inventory.tf is applied
cd multicloud/gcp
terraform state list | grep inventory
```

## Cost Optimization

### Direct VPC Egress Pricing

- **No additional charge** for Direct VPC egress itself
- Standard Cloud Run pricing applies
- **Network egress charges** for data transfer (standard GCP rates)
- Much cheaper than VPC Connector which has:
  - Hourly connector charges
  - Per-GB data transfer charges

### Optimize egress = "PRIVATE_RANGES_ONLY"

This setting ensures:
- Only private traffic (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) goes through VPC
- Public internet traffic goes directly (more efficient)
- Lower latency for public API calls
- Reduced VPC network costs

## Migration from VPC Connector

If you have existing VPC Connector, you can migrate:

```hcl
# OLD (VPC Connector)
vpc_access {
  connector = google_vpc_access_connector.connector.id
  egress    = "PRIVATE_RANGES_ONLY"
}

# NEW (Direct VPC Egress)
vpc_access {
  network_interfaces {
    network    = google_compute_network.inventory_vpc.id
    subnetwork = google_compute_subnetwork.inventory_subnet.id
  }
  egress = "PRIVATE_RANGES_ONLY"
}
```

Benefits:
- ✅ Remove connector resource and costs
- ✅ Better performance
- ✅ Simpler configuration
- ✅ Automatic scaling

## References

- [Cloud Run Direct VPC Egress](https://cloud.google.com/run/docs/configuring/vpc-direct-vpc)
- [VPC Access Overview](https://cloud.google.com/run/docs/configuring/connecting-vpc)
- [Firewall Rules Best Practices](https://cloud.google.com/vpc/docs/firewalls)
- [Cloud Run Network Pricing](https://cloud.google.com/run/pricing#networking)

