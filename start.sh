#!/bin/bash

# ============================================
# Online Boutique — Start Script
# ============================================
# Provisions AWS infrastructure and deploys
# all 12 services in one command.
# Usage: ./start.sh
# ============================================

set -e  # stop if any command fails

echo ""
echo "================================================"
echo "  Online Boutique — Starting Up"
echo "================================================"
echo ""

# ── Step 1: Terraform ──────────────────────────────
echo "▶ Step 1/6 — Provisioning AWS infrastructure..."
echo "  (This takes ~15 minutes — billing starts now)"
echo ""
cd ~/online-boutique/terraform-aws
terraform apply -auto-approve
echo ""
echo "✅ Infrastructure ready!"
echo ""

# ── Step 2: Connect kubectl ────────────────────────
echo "▶ Step 2/6 — Connecting kubectl to cluster..."
aws eks update-kubeconfig --region us-east-1 --name online-boutique-cluster
echo "✅ kubectl connected!"
echo ""

# ── Step 3: Verify nodes ───────────────────────────
echo "▶ Step 3/6 — Waiting for nodes to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s
echo "✅ Nodes are ready!"
echo ""

# ── Step 4: Deploy services ────────────────────────
echo "▶ Step 4/6 — Deploying all 12 services..."
cd ~/online-boutique/k8s
kubectl apply -f .
echo ""

# Scale down shoppingassistantservice (GCP-only)
kubectl scale deployment shoppingassistantservice --replicas=0
echo "✅ Services deployed!"
echo ""

# ── Step 5: Install metrics server ────────────────
echo "▶ Step 5/6 — Installing metrics server..."
kubectl apply -f ~/online-boutique/k8s/metrics-server.yaml 2>/dev/null || \
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]' 2>/dev/null || true
echo "✅ Metrics server installed!"
echo ""

# ── Step 6: Wait for pods + get URL ───────────────
echo "▶ Step 6/6 — Waiting for pods to be running..."
echo "  (Waiting up to 3 minutes for images to pull...)"
sleep 60

kubectl get pods
echo ""

echo "▶ Getting public URL..."
echo ""
kubectl get svc frontend
echo ""

# Extract and display the URL nicely
URL=$(kubectl get svc frontend -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
if [ -n "$URL" ]; then
  echo "================================================"
  echo "  ✅ YOUR WEBSITE IS LIVE!"
  echo ""
  echo "  URL: http://$URL"
  echo "================================================"
else
  echo "  ⏳ Load balancer URL still provisioning..."
  echo "  Run: kubectl get svc frontend"
  echo "  Copy the EXTERNAL-IP once it appears"
  echo "================================================"
fi
echo ""
echo "  Remember to run ./stop.sh when done!"
echo "  AWS is charging ~\$0.18/hour right now."
echo ""
