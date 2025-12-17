# Deploy Online Boutique to a New GCP Project

This guide shows how to deploy the Online Boutique sample app to a brand new Google Cloud project using GKE Autopilot.

## Prerequisites
- gcloud CLI and kubectl installed
- You are authenticated: `gcloud auth login`
- Billing enabled on the project
- Recommended IAM roles for your user:
  - Project Owner (simplest) or
  - Service Usage Admin (`roles/serviceusage.serviceUsageAdmin`) to enable APIs
  - Kubernetes Engine Admin (`roles/container.admin`) to create clusters

## One-command deployment (recommended)
Run from the repo root:

```bash
# Replace with your project and preferred region
AUTO_APPROVE=1 ./deploy-gcp.sh <PROJECT_ID> <REGION>
# Example
AUTO_APPROVE=1 ./deploy-gcp.sh online-boutique-12345 us-central1
```

What the script does:
- Enables APIs: Compute, GKE, Monitoring, Cloud Trace, Cloud Profiler
- Creates a GKE Autopilot cluster
- Fetches cluster credentials
- Applies Kubernetes manifests
- Waits for pods to be ready and prints the frontend URL

## Manual steps (if not using the script)
```bash
PROJECT_ID=<PROJECT_ID>
REGION=us-central1
CLUSTER=online-boutique

# Enable required APIs
gcloud services enable compute.googleapis.com \
  container.googleapis.com monitoring.googleapis.com \
  cloudtrace.googleapis.com cloudprofiler.googleapis.com \
  --project=$PROJECT_ID

# Create Autopilot cluster
gcloud container clusters create-auto $CLUSTER \
  --project=$PROJECT_ID --region=$REGION

# Get credentials
export USE_GKE_GCLOUD_AUTH_PLUGIN=True
gcloud container clusters get-credentials $CLUSTER \
  --region=$REGION --project=$PROJECT_ID

# Deploy
kubectl apply -f ./release/kubernetes-manifests.yaml

# Wait for readiness
kubectl wait --for=condition=available --timeout=600s deployment --all -n default

# Get the frontend public IP
kubectl get service frontend-external -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## Verify
- Open `http://<EXTERNAL_IP>` in your browser.
- Check workloads: `kubectl get pods`
- Check services: `kubectl get svc`

## Load generation
- In-cluster load generator runs by default.
- Scale users (example): `kubectl set env deployment/loadgenerator USERS=50`

## Cleanup
To remove the cluster and avoid costs:
```bash
./cleanup-gcp.sh <PROJECT_ID> <REGION>
# or manually
gcloud container clusters delete online-boutique \
  --project=<PROJECT_ID> --region=<REGION>
```

## Troubleshooting
- Missing plugin: Install GKE auth plugin or set `USE_GKE_GCLOUD_AUTH_PLUGIN=True`.
- Quotas: Ensure sufficient GCE quotas in the chosen region.
- API errors: Confirm required APIs are enabled and billing is active.
