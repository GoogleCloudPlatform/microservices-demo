# Deployment Guide

## Paths

### 1. Local development
- Start the boutique application and local observability stack:
  - `docker compose up -d`
- Start the AEGIS dev control plane:
  - `bash infra/start_platform.sh`
- This path uses:
  - FastAPI with local Python
  - Vite dev server for the dashboard
  - optional demo-mode scoring when models are unavailable

### 2. Local production-style Compose validation
- Start the boutique application and observability stack:
  - `docker compose up -d`
- Start the packaged AEGIS services:
  - `docker compose -f docker-compose.yml -f docker-compose.platform.yml up -d --build`
- Endpoints:
  - backend: `http://localhost:8001`
  - dashboard: `http://localhost:8088`

### 3. Kubernetes (`kind` first)
- Bootstrap cluster and ingress:
  - `bash infra/k8s/bootstrap-kind.sh`
- Build and load local platform images:
  - `bash infra/k8s/build-kind-images.sh`
- Deploy the boutique app:
  - `kubectl apply -f release/kubernetes-manifests.yaml`
- Deploy the AEGIS platform:
  - `bash infra/k8s/deploy-kind.sh`
- Access:
  - add `127.0.0.1 aegis.local` to `/etc/hosts`
  - the dashboard ingress is protected with basic auth from `deploy/platform/base/dashboard-auth.yaml`
  - rotate both the dashboard auth secret and `AEGIS_API_TOKEN` before any non-local use

## Configuration

Environment variables are defined in [.env.example](/Users/ishu/Hackathon/microservices-demo/.env.example). Key production controls:
- `AEGIS_RUNTIME_MODE=production`
- `AEGIS_AUTH_ENABLED=true`
- `AEGIS_API_TOKEN=<strong secret>`
- `AEGIS_ALLOW_DEMO_MODE=false`
- `AEGIS_ALLOWED_ORIGINS=<dashboard origin list>`
- `AEGIS_ORCHESTRATOR=kubernetes`

## Security Notes
- Mutating endpoints require `X-Aegis-Token` when auth is enabled.
- Production mode fails closed when models are missing and demo fallback is disabled.
- The dashboard should talk to the backend through `/api` behind ingress or nginx, not directly to localhost.
- The backend is cluster-internal by default in Kubernetes; only the dashboard is exposed via ingress.
- The production overlay enables TLS-ready ingress configuration and disables wildcard/demo defaults.
