#!/bin/bash

# Multicloud Load Generator Example
# This script demonstrates how to run the load generator against your deployed multicloud services

# ==============================================
# Configuration - Update these with your actual service URLs
# ==============================================

# Replace these with your actual service IP addresses from terraform outputs
AWS_ACCOUNTING_IP="YOUR_AWS_EC2_IP"
AZURE_ANALYTICS_IP="YOUR_AZURE_VM_IP"  
GCP_CRM_IP="YOUR_GCP_INSTANCE_IP"

# Build URLs (port 8080 as specified in the terraform configs)
export AWS_ACCOUNTING_URL="http://${AWS_ACCOUNTING_IP}:8080"
export AZURE_ANALYTICS_URL="http://${AZURE_ANALYTICS_IP}:8080"
export GCP_CRM_URL="http://${GCP_CRM_IP}:8080"

# Optional: Frontend URL for boutique testing
export FRONTEND_ADDR="your-boutique-frontend-url"

# Load testing configuration
export USERS=20                        # Number of concurrent users
export RATE=5                          # Users spawned per second

# ==============================================
# Option 1: Run with Docker
# ==============================================

echo "Building load generator Docker image..."
docker build -t multicloud-loadgen .

echo "Running load tests (boutique + multicloud services)..."
docker run --rm \
  -e AWS_ACCOUNTING_URL="${AWS_ACCOUNTING_URL}" \
  -e AZURE_ANALYTICS_URL="${AZURE_ANALYTICS_URL}" \
  -e GCP_CRM_URL="${GCP_CRM_URL}" \
  -e FRONTEND_ADDR="${FRONTEND_ADDR}" \
  -e USERS="${USERS}" \
  -e RATE="${RATE}" \
  multicloud-loadgen

# ==============================================
# Option 2: Run locally with Python
# ==============================================

# Uncomment to run locally instead of Docker:
# echo "Installing dependencies..."
# pip install -r requirements.txt
# 
# echo "Running load tests locally..."
# locust --host="http://${FRONTEND_ADDR}" --headless -u ${USERS} -r ${RATE}

echo "Load test completed. Check the output above for results."
echo ""
echo "The test will show statistics for:"
echo "- Original boutique tasks (index, setCurrency, browseProduct, etc.)"
echo "- processTransaction: AWS accounting service operations"
echo "- recordMetrics: Azure analytics service operations" 
echo "- manageCustomer: GCP CRM service operations" 