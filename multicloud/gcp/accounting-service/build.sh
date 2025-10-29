#!/bin/bash

# Accounting Service Build and Deploy Script
# This script builds and pushes the accounting service container to Artifact Registry

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project ID
PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project set. Run: gcloud config set project PROJECT_ID${NC}"
    exit 1
fi

echo -e "${GREEN}Using GCP Project: ${PROJECT_ID}${NC}"

# Check if Artifact Registry repo exists
echo -e "${YELLOW}Checking if Artifact Registry repository exists...${NC}"
if ! gcloud artifacts repositories describe accounting-repo --location=us-central1 --project=${PROJECT_ID} &>/dev/null; then
    echo -e "${YELLOW}Creating Artifact Registry repository...${NC}"
    gcloud artifacts repositories create accounting-repo \
        --repository-format=docker \
        --location=us-central1 \
        --description="Accounting service container images" \
        --project=${PROJECT_ID}
    echo -e "${GREEN}Repository created successfully${NC}"
else
    echo -e "${GREEN}Repository already exists${NC}"
fi

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=${PROJECT_ID}
gcloud services enable artifactregistry.googleapis.com --project=${PROJECT_ID}
gcloud services enable run.googleapis.com --project=${PROJECT_ID}

# Build and push using Cloud Build
echo -e "${YELLOW}Building and pushing container image...${NC}"
gcloud builds submit --config=cloudbuild.yaml --project=${PROJECT_ID}

echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "${GREEN}Image available at: us-central1-docker.pkg.dev/${PROJECT_ID}/accounting-repo/accounting-service:latest${NC}"
echo ""
echo -e "${YELLOW}To deploy with Terraform:${NC}"
echo "  cd ../  # Go to multicloud/gcp directory"
echo "  terraform init"
echo "  terraform apply"

