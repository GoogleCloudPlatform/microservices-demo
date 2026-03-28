# AEGIS

![AEGIS Architecture](docs/assets/aegis-architecture.png)

AEGIS is an observability and automated remediation platform built around the Google Online Boutique microservices application. It ingests live service telemetry, converts that telemetry into model features, scores service behavior, detects rising failure risk, evaluates bounded recovery actions, executes remediation through Docker or Kubernetes-aware orchestrators, and exposes the full workflow through a multi-page operations dashboard.

## Contents

- [Overview](#overview)
- [Core Capabilities](#core-capabilities)
- [System Architecture](#system-architecture)
- [Pipeline](#pipeline)
- [Technology Stack](#technology-stack)
- [Repository Layout](#repository-layout)
- [Dashboard Surfaces](#dashboard-surfaces)
- [Quick Start on Localhost](#quick-start-on-localhost)
- [Deployment Modes](#deployment-modes)
- [Public Hosting From This Machine](#public-hosting-from-this-machine)
- [Configuration](#configuration)
- [Authentication and Access](#authentication-and-access)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Documentation](#project-documentation)

## Overview

AEGIS sits between the runtime platform and the operator. Its job is to:

1. collect live runtime, log, and trace-adjacent signals
2. build per-service behavioral windows
3. score risk with the trained Isolation Forest and LSTM models in `models/aegis_models`
4. surface current health, predictive alerts, and historical evidence
5. run bounded remediation workflows when services degrade
6. persist incidents, logs, events, demo runs, and reports for later review

The repository includes the application layer, the observability stack, the AEGIS backend, the React dashboard, deployment manifests, and the model runtime integration.

## Core Capabilities

- Live telemetry ingestion and sliding-window state
- Model-backed anomaly scoring
- Pre-failure prediction using LSTM sequence inference
- Heuristic root-cause estimation
- Policy-based remediation and containment
- Persistent incident memory and system log storage
- Autonomous demo workflow with attack, recovery, timeline, and downloadable report
- Docker runtime support
- Kubernetes deployment and workload recovery path

## System Architecture

```text
Online Boutique microservices
        ↓
Runtime platform (Docker or Kubernetes)
        ↓
Prometheus / Loki / Promtail / Jaeger / Grafana
        ↓
AEGIS ingestion + feature extraction
        ↓
Isolation Forest + LSTM inference
        ↓
Root-cause analysis + action policy engine
        ↓
Execution + evaluation + containment
        ↓
Incident memory + event store + operator dashboard
```

AEGIS is organized as three layers:

- `src/`: the Google Online Boutique application services
- `observability/` and `deploy/platform/`: telemetry and platform deployment assets
- `backend/`, `ml/`, `dashboard/`, and `pipeline/`: the AEGIS control plane

## Pipeline

### 1. Ingestion

The backend continuously ingests runtime and observability signals into a sliding window for each service.

### 2. Feature Conversion

The backend converts recent observations into:

- service-level summaries for the UI
- rule-oriented indicators for remediation
- model feature vectors and sequences for inference

### 3. Model Scoring

AEGIS runs two scoring paths:

- Isolation Forest for point-in-time anomaly detection
- LSTM for sequence-aware failure risk prediction

### 4. Root-Cause Estimation

The correlation engine uses service dependencies and score propagation to estimate the most likely source of disruption.

### 5. Action Selection

The remediation engine validates an action against policy, cooldown, retry budget, and orchestrator capabilities before executing it.

### 6. Execution and Evaluation

The selected action runs through the active orchestrator adapter. AEGIS then evaluates whether health, readiness, and anomaly pressure improved.

### 7. Containment and Escalation

If recovery is incomplete, AEGIS can retry, contain, isolate, or escalate according to service and failure policy.

### 8. Persistence and Reporting

Events, logs, incidents, demo runs, and reports are persisted into SQLite-backed stores and surfaced through the dashboard and report endpoints.

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- SQLite
- Docker SDK
- Kubernetes Python client

### ML Runtime

- scikit-learn
- PyTorch
- NumPy
- pandas

### Frontend

- React 18
- Vite
- D3
- ESLint
- Vitest

### Observability

- Prometheus
- Loki
- Promtail
- Jaeger
- Grafana
- kube-state-metrics
- node-exporter
- cAdvisor
- redis-exporter
- OpenTelemetry Collector manifests

### Deployment

- Docker Compose
- Kubernetes manifests with Kustomize overlays
- kind for local cluster proving
- NGINX for packaged dashboard serving

## Repository Layout

```text
backend/              FastAPI backend, remediation engine, persistence
dashboard/            React dashboard
deploy/platform/      Kubernetes platform manifests
docs/                 Deployment, telemetry, proving, and audit docs
infra/                Startup scripts, kind helpers, ngrok example config
ml/                   Model runtime and training code
models/aegis_models/  Runtime model artifacts
observability/        Prometheus, Loki, Promtail, Grafana configs
pipeline/             Data collection and dataset preparation scripts
release/              Application deployment manifests
src/                  Google Online Boutique microservices
```

## Dashboard Surfaces

AEGIS exposes four primary views:

- `Solar System`: live service topology, anomalies, recommendations, predictive alerts, and service drilldown
- `Infrastructure`: cluster and workload state, observability status, remediation state, and memory context
- `Model Insights`: service scores, feature pressure, sequence trends, and predictive readiness
- `System Logs`: persisted events, backend logs, demo summaries, reports, and timeline playback

## Quick Start on Localhost

### Prerequisites

- Docker Desktop or Docker Engine
- Python 3
- Node.js and npm

### 1. Start the application and observability stack

```bash
cd /Users/ishu/Hackathon/microservices-demo
docker compose up -d
```

### 2. Start the AEGIS backend and dashboard

```bash
bash infra/start_platform.sh
```

### 3. Open the local endpoints

- Storefront: `http://localhost:8080`
- AEGIS dashboard: `http://localhost:5173`
- Backend docs: `http://localhost:8001/docs`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Jaeger: `http://localhost:16686`

### 4. Verify health

```bash
curl http://localhost:8001/health
curl http://localhost:8001/infrastructure
curl http://localhost:8001/ml/insights
```

### 5. Run the autonomous demo

Use `RUN DEMO` in the dashboard. The platform will:

- intentionally disrupt `recommendationservice`
- detect degradation
- execute the recovery workflow
- update the timeline and logs
- generate a persisted summary report

### 6. Stop the platform

```bash
bash infra/stop_platform.sh
docker compose down
```

## Deployment Modes

### Local development

```bash
docker compose up -d
bash infra/start_platform.sh
```

### Local packaged deployment

```bash
docker compose up -d
docker compose -f docker-compose.yml -f docker-compose.platform.yml up -d --build
```

Packaged endpoints:

- dashboard: `http://localhost:8088`
- backend: `http://localhost:8001`

### Kubernetes with kind

```bash
bash infra/k8s/bootstrap-kind.sh
bash infra/k8s/build-kind-images.sh
kubectl apply -f release/kubernetes-manifests.yaml
bash infra/k8s/deploy-kind.sh
```

Additional deployment detail is in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Public Hosting From This Machine

The supported public path is:

1. run the base stack locally with Docker
2. run the packaged AEGIS backend and dashboard
3. expose the dashboard over HTTPS with ngrok
4. keep the backend private behind the dashboard reverse proxy

Quick path:

```bash
docker compose up -d
docker compose --env-file .env.public -f docker-compose.platform.yml up -d --build
ngrok http 8088
```

Full instructions are in [docs/PUBLIC_HOSTING.md](docs/PUBLIC_HOSTING.md).

## Configuration

Start with [.env.example](.env.example) for local development and [.env.public.example](.env.public.example) for packaged public hosting.

Key variables:

- `AEGIS_RUNTIME_MODE`
- `AEGIS_ENVIRONMENT`
- `AEGIS_CLUSTER_NAME`
- `AEGIS_ALLOWED_ORIGINS`
- `AEGIS_AUTH_ENABLED`
- `AEGIS_API_TOKEN`
- `AEGIS_ORCHESTRATOR`
- `AEGIS_K8S_NAMESPACE`
- `AEGIS_MODEL_DIR`
- `AEGIS_SYSTEM_DB`
- `AEGIS_PROMETHEUS_URL`
- `AEGIS_LOKI_URL`
- `AEGIS_PROMTAIL_URL`
- `AEGIS_JAEGER_URL`
- `AEGIS_GRAFANA_URL`
- `AEGIS_OTEL_COLLECTOR_URL`
- `AEGIS_REMEDIATION_COOLDOWN_S`
- `AEGIS_REMEDIATION_LOCK_TIMEOUT_S`
- `AEGIS_INCIDENT_MEMORY_LIMIT`
- `AEGIS_INCIDENT_MEMORY_RETENTION_DAYS`
- `AEGIS_PREDICTIVE_ALERT_THRESHOLD`
- `AEGIS_PREDICTIVE_AUTO_ACTION_THRESHOLD`
- `AEGIS_PREDICTIVE_ACTION_COOLDOWN_S`

## Authentication and Access

Current runtime access is intentionally simple:

- the working prototype is open by default
- operator endpoints can be protected with `AEGIS_API_TOKEN`
- the packaged dashboard proxies API traffic through `/api`
- browser Google sign-in code exists in the repository but is currently disabled in the live runtime

## API Endpoints

Primary endpoints:

- `GET /health`
- `GET /status`
- `GET /topology`
- `GET /infrastructure`
- `GET /ml/insights`
- `GET /events`
- `GET /logs`
- `GET /logs/report`
- `GET /history`
- `GET /window/{service}`
- `GET /incidents/active`
- `GET /incidents/history`
- `GET /incidents/similar`
- `POST /decision/validate`
- `POST /remediate`
- `POST /demo/run`
- `POST /incidents/{incident_id}/acknowledge`

## Testing

Backend:

```bash
python3 -m unittest discover -s backend/tests -p 'test_*.py'
python3 -m py_compile backend/anomaly_api/*.py backend/remediation/*.py
```

Frontend:

```bash
cd dashboard
npm run lint
npm test
npm run build
```

Kubernetes manifests:

```bash
kubectl kustomize deploy/platform/overlays/kind
kubectl kustomize deploy/platform/overlays/production
```

## Project Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [Public Hosting Guide](docs/PUBLIC_HOSTING.md)
- [Telemetry Coverage](docs/TELEMETRY.md)
- [Kubernetes Proving Notes](docs/KIND_PROVING.md)
- [Production Audit](docs/PRODUCTION_AUDIT.md)
