#!/bin/bash

# Script to update loadgenerator configuration for the correct PSC endpoint region
# Usage: ./update-loadgenerator-region.sh <region> <psc-ip>
# Example: ./update-loadgenerator-region.sh us-west1 10.138.0.100

REGION=$1
PSC_IP=$2

if [ -z "$REGION" ] || [ -z "$PSC_IP" ]; then
    echo "Usage: $0 <region> <psc-ip>"
    echo "Example: $0 us-west1 10.138.0.100"
    echo ""
    echo "To get the PSC IP for your region:"
    echo "  us-central1: terraform output inventory_psc_endpoint_ip"
    echo "  us-west1:    terraform output inventory_psc_endpoint_ip_west"
    exit 1
fi

echo "🔄 Updating loadgenerator configuration for region: $REGION"
echo "🔗 PSC Endpoint IP: $PSC_IP"

# Update configuration files
GCP_INVENTORY_URL="http://$PSC_IP:8080"

echo "📝 Updating configuration files..."

# Update multicloud-config.yaml
sed -i.bak "s|GCP_INVENTORY_URL:.*|GCP_INVENTORY_URL: \"$GCP_INVENTORY_URL\"|" src/loadgenerator/multicloud-config.yaml

# Update multicloud-env.sh  
sed -i.bak "s|export GCP_INVENTORY_URL=.*|export GCP_INVENTORY_URL=\"$GCP_INVENTORY_URL\"|" src/loadgenerator/multicloud-env.sh

# Update multicloud-example.sh
sed -i.bak "s|export GCP_INVENTORY_URL=.*|export GCP_INVENTORY_URL=\"$GCP_INVENTORY_URL\"|" src/loadgenerator/multicloud-example.sh

# Update kubernetes manifests
sed -i.bak "s|value: \"http://[0-9.]*:8080\"|value: \"$GCP_INVENTORY_URL\"|" kubernetes-manifests/loadgenerator.yaml
sed -i.bak "s|value: \"http://[0-9.]*:8080\"|value: \"$GCP_INVENTORY_URL\"|" kustomize/base/loadgenerator.yaml

echo "✅ Configuration updated! Files modified:"
echo "  - src/loadgenerator/multicloud-config.yaml"
echo "  - src/loadgenerator/multicloud-env.sh"
echo "  - src/loadgenerator/multicloud-example.sh"
echo "  - kubernetes-manifests/loadgenerator.yaml"
echo "  - kustomize/base/loadgenerator.yaml"

echo ""
echo "📊 Current configuration:"
echo "  Region: $REGION"
echo "  PSC Endpoint: $PSC_IP"
echo "  Service URL: $GCP_INVENTORY_URL"

echo ""
echo "🚀 Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Deploy: kubectl apply -f kubernetes-manifests/loadgenerator.yaml"
echo "  3. Test: kubectl logs -f deployment/loadgenerator | grep Inventory"

echo ""
echo "💡 Backup files created with .bak extension" 