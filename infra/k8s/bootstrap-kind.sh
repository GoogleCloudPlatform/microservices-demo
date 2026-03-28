#!/usr/bin/env bash
set -euo pipefail

if ! command -v kind >/dev/null 2>&1; then
  echo "kind is required but not installed"
  exit 1
fi

CLUSTER_NAME="${CLUSTER_NAME:-aegis}"

kind create cluster --name "${CLUSTER_NAME}" --wait 120s
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx --for=condition=Available deployment/ingress-nginx-controller --timeout=180s

echo "kind cluster ${CLUSTER_NAME} is ready"
