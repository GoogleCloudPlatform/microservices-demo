#!/bin/bash

# ============================================
# Online Boutique — Start Script
# ============================================
# Provisions AWS infrastructure, deploys all
# 12 services, installs ALB Ingress Controller,
# Prometheus + Grafana + Loki monitoring.
# Usage: ./start.sh
# ============================================

set -e  # stop if any command fails

echo ""
echo "================================================"
echo "  Online Boutique — Starting Up"
echo "================================================"
echo ""

# ── Step 1: Terraform ──────────────────────────────
echo "▶ Step 1/9 — Provisioning AWS infrastructure..."
echo "  (This takes ~15 minutes — billing starts now)"
echo ""
cd ~/online-boutique/terraform-aws
terraform apply -auto-approve
echo ""
echo "✅ Infrastructure ready!"
echo ""

# ── Step 2: Connect kubectl ────────────────────────
echo "▶ Step 2/9 — Connecting kubectl to cluster..."
aws eks update-kubeconfig --region us-east-1 --name online-boutique-cluster
echo "✅ kubectl connected!"
echo ""

# ── Step 3: Verify nodes ───────────────────────────
echo "▶ Step 3/9 — Waiting for nodes to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s
echo "✅ Nodes are ready!"
echo ""

# ── Step 4: Install AWS Load Balancer Controller ───
echo "▶ Step 4/9 — Installing AWS Load Balancer Controller..."
helm repo add eks https://aws.github.io/eks-charts 2>/dev/null || true
helm repo update

VPC_ID=$(aws ec2 describe-vpcs --region us-east-1 \
  --filters "Name=tag:Name,Values=online-boutique-vpc" \
  --query 'Vpcs[0].VpcId' --output text)

ALB_ROLE_ARN=$(cd ~/online-boutique/terraform-aws && terraform output -raw aws_lbc_role_arn)

if ! helm status aws-load-balancer-controller -n kube-system &>/dev/null; then
  helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=online-boutique-cluster \
    --set serviceAccount.create=true \
    --set "serviceAccount.annotations.eks\.amazonaws\.com/role-arn=${ALB_ROLE_ARN}" \
    --set region=us-east-1 \
    --set vpcId=$VPC_ID
else
  echo "  (ALB controller already installed, skipping)"
fi

echo "  Waiting for ALB controller to be ready..."
kubectl wait --for=condition=Ready pod \
  -l app.kubernetes.io/name=aws-load-balancer-controller \
  -n kube-system --timeout=120s
echo "✅ AWS Load Balancer Controller ready!"
echo ""

# ── Step 5: Deploy services ────────────────────────
echo "▶ Step 5/9 — Deploying all 12 services..."
cd ~/online-boutique/k8s
kubectl apply -f .
kubectl scale deployment shoppingassistantservice --replicas=0
echo "✅ Services deployed!"
echo ""

# ── Step 6: Install metrics server ────────────────
echo "▶ Step 6/9 — Installing metrics server..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml 2>/dev/null || true
sleep 5
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]' 2>/dev/null || true
echo "✅ Metrics server installed!"
echo ""

# ── Step 7: Install Prometheus + Grafana ──────────
echo "▶ Step 7/9 — Installing Prometheus + Grafana..."
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

# ── Step 8: Install Loki ──────────────────────────
echo "▶ Step 8/9 — Installing Loki..."
if ! helm status loki -n monitoring &>/dev/null; then
  helm install loki grafana/loki-stack \
    --namespace monitoring \
    --set grafana.enabled=false \
    --set prometheus.enabled=false
else
  echo "  (Loki already installed, skipping)"
fi

kubectl wait --for=condition=Ready pod \
  -l "app=loki" \
  -n monitoring --timeout=180s 2>/dev/null || sleep 60

kubectl rollout restart daemonset/loki-promtail -n monitoring 2>/dev/null || true
echo "✅ Loki installed!"
echo ""

# ── Step 9: Add Loki datasource to Grafana ────────
echo "▶ Step 9/9 — Adding Loki as Grafana datasource..."
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

# Get Ingress URL
INGRESS_URL=$(kubectl get ingress frontend-ingress \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)

echo "  Website (via ALB Ingress):"
if [ -n "$INGRESS_URL" ]; then
  echo "  http://$INGRESS_URL"
else
  echo "  Run: kubectl get ingress (URL still provisioning)"
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
