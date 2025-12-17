#!/bin/bash
# =============================================================================
# Online Boutique - GCP Deployment Script
# =============================================================================
# This script deploys the Online Boutique microservices demo to Google Cloud
# Platform using Google Kubernetes Engine (GKE) Autopilot.
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - kubectl installed
#   - Billing enabled on the GCP project
#
# Usage:
#   ./deploy-gcp.sh [PROJECT_ID] [REGION]
#
# Examples:
#   ./deploy-gcp.sh my-project-id us-central1
#   ./deploy-gcp.sh my-project-id  # Uses default region: us-central1
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${2:-us-central1}"
CLUSTER_NAME="online-boutique"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
print_step() {
    echo -e "\n${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

print_error() {
    echo -e "${RED}Error:${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is required but not installed."
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Pre-flight Checks
# -----------------------------------------------------------------------------
print_step "Running pre-flight checks..."

check_command gcloud
check_command kubectl

if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID is required. Usage: ./deploy-gcp.sh PROJECT_ID [REGION]"
    exit 1
fi

echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Cluster Name: $CLUSTER_NAME"

# Confirm deployment (can be skipped with AUTO_APPROVE=1)
if [ "${AUTO_APPROVE}" != "1" ]; then
    read -p "Do you want to proceed with deployment? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
else
    echo "AUTO_APPROVE=1 set; proceeding without interactive confirmation."
fi

# -----------------------------------------------------------------------------
# Step 1: Enable Required APIs
# -----------------------------------------------------------------------------
print_step "Enabling required Google Cloud APIs..."

gcloud services enable compute.googleapis.com \
    container.googleapis.com \
    monitoring.googleapis.com \
    cloudtrace.googleapis.com \
    cloudprofiler.googleapis.com \
    --project="${PROJECT_ID}"

echo "  APIs enabled successfully."

# -----------------------------------------------------------------------------
# Step 2: Create GKE Autopilot Cluster
# -----------------------------------------------------------------------------
print_step "Creating GKE Autopilot cluster '${CLUSTER_NAME}'..."

# Check if cluster already exists
if gcloud container clusters describe "${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    print_warning "Cluster '${CLUSTER_NAME}' already exists. Skipping creation."
else
    gcloud container clusters create-auto "${CLUSTER_NAME}" \
        --project="${PROJECT_ID}" \
        --region="${REGION}"
    echo "  Cluster created successfully."
fi

# -----------------------------------------------------------------------------
# Step 3: Get Cluster Credentials
# -----------------------------------------------------------------------------
print_step "Getting cluster credentials..."

export USE_GKE_GCLOUD_AUTH_PLUGIN=True
gcloud container clusters get-credentials "${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}"

echo "  Credentials configured successfully."

# -----------------------------------------------------------------------------
# Step 4: Deploy Online Boutique Services
# -----------------------------------------------------------------------------
print_step "Deploying Online Boutique microservices..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Apply the Kubernetes manifests
kubectl apply -f "${SCRIPT_DIR}/release/kubernetes-manifests.yaml"

echo "  Services deployed successfully."

# -----------------------------------------------------------------------------
# Step 5: Wait for Pods to be Ready
# -----------------------------------------------------------------------------
print_step "Waiting for all pods to be ready (this may take 5-10 minutes)..."

# Wait for all deployments to be ready
kubectl wait --for=condition=available --timeout=600s deployment --all -n default

echo "  All pods are ready."

# -----------------------------------------------------------------------------
# Step 6: Get External IP
# -----------------------------------------------------------------------------
print_step "Getting frontend external IP..."

# Wait for external IP to be assigned
EXTERNAL_IP=""
MAX_RETRIES=30
RETRY_COUNT=0

while [ -z "$EXTERNAL_IP" ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    EXTERNAL_IP=$(kubectl get service frontend-external -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
    if [ -z "$EXTERNAL_IP" ]; then
        echo "  Waiting for external IP... (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
        sleep 10
        ((RETRY_COUNT++))
    fi
done

if [ -z "$EXTERNAL_IP" ]; then
    print_error "Failed to get external IP after $MAX_RETRIES attempts."
    exit 1
fi

# -----------------------------------------------------------------------------
# Deployment Complete
# -----------------------------------------------------------------------------
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  ${BLUE}Frontend URL:${NC} http://${EXTERNAL_IP}"
echo ""
echo "  Cluster Details:"
echo "    Name: ${CLUSTER_NAME}"
echo "    Project: ${PROJECT_ID}"
echo "    Region: ${REGION}"
echo ""
echo "  Useful Commands:"
echo "    kubectl get pods              # View all pods"
echo "    kubectl get services          # View all services"
echo "    kubectl logs <pod-name>       # View pod logs"
echo ""
echo -e "  ${YELLOW}To delete resources:${NC}"
echo "    gcloud container clusters delete ${CLUSTER_NAME} \\"
echo "      --project=${PROJECT_ID} --region=${REGION}"
echo ""
