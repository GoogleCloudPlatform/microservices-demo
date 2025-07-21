#!/bin/bash

# Multicloud Service Environment Variables
# Source this file to set environment variables for local testing
# Usage: source multicloud-env.sh

export AWS_ACCOUNTING_URL="http://54.163.148.73:8080"
export AZURE_ANALYTICS_URL="http://20.160.153.10:8080"
export GCP_CRM_URL="http://10.2.0.2:8080"
export GCP_INVENTORY_URL="http://10.132.0.21:8080"

# Optional: Set load testing parameters
export USERS=20
export RATE=5
export FRONTEND_ADDR="frontend:80"

echo "✅ Multicloud environment variables set:"
echo "   AWS_ACCOUNTING_URL: $AWS_ACCOUNTING_URL"
echo "   AZURE_ANALYTICS_URL: $AZURE_ANALYTICS_URL"
echo "   GCP_CRM_URL: $GCP_CRM_URL"
echo ""
echo "🚀 Ready for local testing!"
echo "   Run: locust --host=\"http://\$FRONTEND_ADDR\" --headless -u \$USERS -r \$RATE" 