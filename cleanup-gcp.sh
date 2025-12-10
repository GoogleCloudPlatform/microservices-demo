#!/bin/bash
# =============================================================================
# Online Boutique - GCP Cleanup Script
# =============================================================================
# This script removes all resources created by the deploy-gcp.sh script.
#
# Usage:
#   ./cleanup-gcp.sh [PROJECT_ID] [REGION]
#
# Examples:
#   ./cleanup-gcp.sh my-project-id us-central1
#   ./cleanup-gcp.sh  # Uses current gcloud project config
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

print_step() {
    echo -e "\n${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

print_error() {
    echo -e "${RED}Error:${NC} $1"
}

if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID is required. Usage: ./cleanup-gcp.sh PROJECT_ID [REGION]"
    exit 1
fi

echo ""
echo -e "${RED}============================================${NC}"
echo -e "${RED}  WARNING: This will delete resources!${NC}"
echo -e "${RED}============================================${NC}"
echo ""
echo "  The following will be deleted:"
echo "    - GKE Cluster: ${CLUSTER_NAME}"
echo "    - All deployed pods and services"
echo "    - Associated load balancers"
echo ""
echo "  Project: ${PROJECT_ID}"
echo "  Region: ${REGION}"
echo ""

read -p "Are you sure you want to proceed? (type 'yes' to confirm) " -r
echo
if [[ ! $REPLY == "yes" ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# -----------------------------------------------------------------------------
# Delete GKE Cluster
# -----------------------------------------------------------------------------
print_step "Deleting GKE cluster '${CLUSTER_NAME}'..."

if gcloud container clusters describe "${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    
    gcloud container clusters delete "${CLUSTER_NAME}" \
        --project="${PROJECT_ID}" \
        --region="${REGION}" \
        --quiet
    
    echo "  Cluster deleted successfully."
else
    print_warning "Cluster '${CLUSTER_NAME}' not found. Nothing to delete."
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Cleanup Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "  All Online Boutique resources have been removed."
echo ""
