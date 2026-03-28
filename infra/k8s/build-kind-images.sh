#!/usr/bin/env bash
set -euo pipefail

if ! command -v kind >/dev/null 2>&1; then
  echo "kind is required but not installed"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CLUSTER_NAME="${CLUSTER_NAME:-aegis}"

docker build -f "${REPO_ROOT}/backend/Dockerfile" -t aegis-backend:dev "${REPO_ROOT}"
docker build -f "${REPO_ROOT}/dashboard/Dockerfile" -t aegis-dashboard:dev "${REPO_ROOT}"

kind load docker-image --name "${CLUSTER_NAME}" aegis-backend:dev
kind load docker-image --name "${CLUSTER_NAME}" aegis-dashboard:dev
