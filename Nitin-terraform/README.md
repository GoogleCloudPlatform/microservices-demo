# Deploying Google Cloud Microservices Demo with Terraform

This document provides a detailed guide to deploying the Google Cloud Microservices Demo application using Terraform and Helm. It covers creating a GKE cluster, deploying microservices, and ensuring the application is accessible via a public URL.

---

## Prerequisites

1. **Google Cloud Platform (GCP) Setup**:
   - Ensure you have a GCP project and billing enabled.
   - Install and authenticate the `gcloud` CLI.

2. **Terraform Installation**:
   - Install Terraform from the [official website](https://developer.hashicorp.com/terraform/downloads).

3. **Other Required Tools**:
   - Install `kubectl` for cluster management.
   - Install `helm` for deploying Helm charts.


---

## Steps

### 1. Create GKE Cluster with Terraform

#### Terraform Configuration

Create a `main.tf` file with the following configuration:

```hcl
provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_container_cluster" "primary" {
  name     = "microservices-cluster"
  location = var.region

  node_config {
    machine_type = var.node_machine_type
    preemptible  = false
  }

  initial_node_count = var.node_count
}

variable "project_id" {}
variable "region" {
  default = "asia-south1-a"
}
variable "node_machine_type" {
  default = "e2-medium"
}
variable "node_count" {
  default = 4
}
```

#### Initialize and Deploy

1. **Initialize Terraform**:
   ```bash
   terraform init
   ```

2. **Validate Configuration**:
   ```bash
   terraform validate
   ```

3. **Deploy Infrastructure**:
   ```bash
   terraform apply
   ```

4. **Connect to the Cluster**:
   ```bash
   gcloud container clusters get-credentials microservices-cluster --region asia-south1-a
   ```

### 2. Deploy Microservices via Helm

#### Add Helm Repository

```bash
helm repo add microservices-demo https://googlecloudplatform.github.io/microservices-demo/
helm repo update
```

#### Deploy Helm Chart

```bash
helm install onlineboutique microservices-demo/onlineboutique \
  --namespace online-boutique --create-namespace \
  -f values.yaml
```

#### Confirm Deployment

Check if all pods are running:
```bash
kubectl get pods -n online-boutique
```

Expose the frontend service:
```bash
kubectl expose deployment frontend \
  --type=LoadBalancer \
  --name=frontend-lb \
  --namespace=online-boutique
```
Retrieve the external IP:
```bash
kubectl get services -n online-boutique
```

Access the application at `http://EXTERNAL_IP`.

---

#### Tools for Optimization

- Use `kubectl top` to monitor resource usage:
  ```bash
  kubectl top pods -n online-boutique
  ```
  
