# AKS Deployment Guide

## Prerequisites

```bash
brew install azure-cli kubectl skaffold terraform
```

## 1. Azure Login

```bash
az login
```

## 2. Provision ACR (Terraform)

```bash
cd terraform-aks
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — set subscription_id, acr_name (must be globally unique)
terraform init
terraform plan -out=plan.out
terraform apply plan.out
```

> **Note:** Terraform only manages the ACR registry. The AKS cluster is created separately via az CLI.

## 3. Create the AKS Cluster

Use the command printed by `terraform output create_aks_cluster`, or run:

```bash
az aks create \
  --name online-boutique \
  --resource-group online-boutique \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --attach-acr <acr-name> \
  --generate-ssh-keys
```

The `--attach-acr` flag grants the cluster's managed identity `AcrPull` access automatically. Takes ~5 minutes.

### Verify

```bash
az aks get-credentials --resource-group online-boutique --name online-boutique
kubectl get nodes
```

## 4. Authenticate Docker to ACR

Required before the first push.

```bash
az acr login --name <acr-name>
```

## 5. Deploy the App

```bash
cd /path/to/microservices-demo
skaffold run -p aks --default-repo=<acr-name>.azurecr.io
```

The ACR login server is printed by `terraform output acr_login_server`.

### Get the frontend URL

```bash
kubectl get service frontend-external
```

Open the `EXTERNAL-IP` in a browser. Allow 1-2 minutes for the load balancer to become reachable.

## Teardown

```bash
# Delete the app from the cluster
skaffold delete -p aks

# Delete the cluster
az aks delete --name online-boutique --resource-group online-boutique --yes

# Delete ACR + resource group
cd terraform-aks && terraform destroy
```

## Troubleshooting

| Error | Fix |
|---|---|
| `no basic auth credentials` | Docker is not authenticated to ACR. Run `az acr login --name <acr-name>`. |
| `repository does not exist` | ACR not provisioned. Run `terraform apply -auto-approve` in `terraform-aks/`. |
| `The subscription is not registered` | Run `az provider register --namespace Microsoft.ContainerRegistry` and retry. |
| `command not found: skaffold` | `brew install skaffold` |
| `acr_name` must be unique | ACR names are globally unique across all Azure. Change `acr_name` in `terraform.tfvars`. |
