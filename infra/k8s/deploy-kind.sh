#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

kubectl apply -f "${REPO_ROOT}/release/kubernetes-manifests.yaml"
kubectl apply -k "${REPO_ROOT}/deploy/platform/overlays/kind"

echo "Platform deployed. Add '127.0.0.1 aegis.local' to /etc/hosts and port-forward ingress if needed."
