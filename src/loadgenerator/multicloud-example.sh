#!/bin/bash

# Multicloud Load Generator Example
# This script demonstrates how to run the load generator against your deployed multicloud services

# ==============================================
# Configuration - Actual multicloud service URLs
# ==============================================

# Actual service URLs from your terraform deployments
export AWS_ACCOUNTING_URL="http://54.163.148.73:8080"     # AWS EC2 Accounting Service
export AZURE_ANALYTICS_URL="http://20.160.153.10:8080"   # Azure VM Analytics Service
export GCP_CRM_URL="http://10.2.0.2:8080"             # GCP Instance CRM Service (private IP)
export GCP_INVENTORY_URL="http://10.132.0.21:8080"        # GCP Inventory Service (PSC europe-west1)

# Optional: Frontend URL for boutique testing
export FRONTEND_ADDR="frontend:80"

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
echo "- Multicloud tasks:"
echo "  - processTransaction (AWS Accounting)"
echo "  - recordMetrics (Azure Analytics)" 
echo "  - manageCustomer (GCP CRM)"
echo "  - checkInventory (GCP Inventory via PSC)"
echo "- processTransaction: AWS accounting service operations (${AWS_ACCOUNTING_URL})"
echo "- recordMetrics: Azure analytics service operations (${AZURE_ANALYTICS_URL})" 
echo "- manageCustomer: GCP CRM service operations via VPC peering (${GCP_CRM_URL})"
echo "- checkInventory: GCP inventory service operations via PSC (${GCP_INVENTORY_URL})" 