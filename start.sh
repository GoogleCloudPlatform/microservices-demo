#!/bin/bash

# ============================================
# Online Boutique — Start Script
# ============================================
# Provisions AWS infrastructure, deploys all
# 12 services, installs Prometheus + Grafana
# + Loki, and adds Loki as a datasource.
# Usage: ./start.sh
# ============================================

set -e  # stop if any command fails

echo ""
echo "================================================"
echo "  Online Boutique — Starting Up"
echo "================================================"
echo ""

# ── Step 1: Terraform ──────────────────────────────
echo "▶ Step 1/8 — Provisioning AWS infrastructure..."
echo "  (This takes ~15 minutes — billing starts now)"
echo ""
cd ~/online-boutique/terraform-aws
terraform apply -auto-approve
echo ""
echo "✅ Infrastructure ready!"
echo ""

# ── Step 2: Connect kubectl ────────────────────────
echo "▶ Step 2/8 — Connecting kubectl to cluster..."
aws eks update-kubeconfig --region us-east-1 --name online-boutique-cluster
echo "✅ kubectl connected!"
echo ""

# ── Step 3: Verify nodes ───────────────────────────
echo "▶ Step 3/8 — Waiting for nodes to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s
echo "✅ Nodes are ready!"
echo ""

# ── Step 4: Deploy services ────────────────────────
echo "▶ Step 4/8 — Deploying all 12 services..."
cd ~/online-boutique/k8s
kubectl apply -f .
kubectl scale deployment shoppingassistantservice --replicas=0
echo "✅ Services deployed!"
echo ""

# ── Step 5: Install metrics server ────────────────
echo "▶ Step 5/8 — Installing metrics server..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml 2>/dev/null || true
sleep 5
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]' 2>/dev/null || true
echo "✅ Metrics server installed!"
echo ""

# ── Step 6: Install Prometheus + Grafana ──────────
echo "▶ Step 6/8 — Installing Prometheus + Grafana..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo add grafana https://grafana.github.io/helm-charts 2>/dev/null || true
helm repo update

kubectl create namespace monitoring 2>/dev/null || true

if ! helm status monitoring -n monitoring &>/dev/null; then
  helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring
else
  echo "  (Prometheus already installed, skipping)"
fi

echo "  Waiting for Grafana to be ready..."
kubectl wait --for=condition=Ready pod \
  -l "app.kubernetes.io/name=grafana" \
  -n monitoring --timeout=300s
echo "✅ Prometheus + Grafana ready!"
echo ""

# ── Step 7: Install Loki ──────────────────────────
echo "▶ Step 7/8 — Installing Loki..."
if ! helm status loki -n monitoring &>/dev/null; then
  helm install loki grafana/loki-stack \
    --namespace monitoring \
    --set grafana.enabled=false \
    --set prometheus.enabled=false
else
  echo "  (Loki already installed, skipping)"
fi

echo "  Waiting for Loki to be ready..."
kubectl wait --for=condition=Ready pod \
  -l "app=loki" \
  -n monitoring --timeout=180s 2>/dev/null || sleep 60

kubectl rollout restart daemonset/loki-promtail -n monitoring 2>/dev/null || true
echo "✅ Loki installed!"
echo ""

# ── Step 8: Add Loki datasource to Grafana ────────
echo "▶ Step 8/8 — Adding Loki as Grafana datasource..."
sleep 15

GRAFANA_PASSWORD=$(kubectl --namespace monitoring get secrets monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d)

GRAFANA_AUTH=$(echo -n "admin:$GRAFANA_PASSWORD" | base64)

kubectl exec -n monitoring deployment/monitoring-grafana -c grafana -- \
  wget -qO- \
  --post-data='{"name":"Loki","type":"loki","url":"http://loki.monitoring:3100","access":"proxy","isDefault":false}' \
  --header='Content-Type: application/json' \
  --header="Authorization: Basic $GRAFANA_AUTH" \
  http://localhost:3000/api/datasources 2>/dev/null || \
  echo "  (Loki datasource may already exist, skipping)"

echo "✅ Loki datasource added!"
echo ""

# ── Final Summary ─────────────────────────────────
echo "================================================"
echo "  ALL DONE!"
echo "================================================"
echo ""

URL=$(kubectl get svc frontend \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)

echo "  Website:"
if [ -n "$URL" ]; then
  echo "  http://$URL"
else
  echo "  Run: kubectl get svc frontend"
fi
echo ""
echo "  Grafana: http://localhost:3000"
echo "  Username: admin"
echo "  Password: $GRAFANA_PASSWORD"
echo ""
echo "  To access Grafana, run in a NEW terminal:"
echo "  export POD_NAME=\$(kubectl --namespace monitoring get pod -l 'app.kubernetes.io/name=grafana,app.kubernetes.io/instance=monitoring' -oname)"
echo "  kubectl --namespace monitoring port-forward \$POD_NAME 3000"
echo ""
echo "  AWS charging ~\$0.18/hour — run ./stop.sh when done!"
echo "================================================"
echo ""
kubectl get pods
