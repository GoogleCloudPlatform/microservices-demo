# AEGIS

AEGIS is an observability, prediction, and automated remediation control plane built on top of Google’s Online Boutique microservices demo. It watches live service telemetry, converts that telemetry into model-ready features, scores service behavior with trained models, runs heuristic root-cause analysis, executes bounded remediation workflows, records what happened, and exposes the whole flow through a multi-page operational dashboard.

This repository is no longer using fake runtime scoring. The backend expects and uses real uploaded artifacts from [models/aegis_models](/Users/ishu/Hackathon/microservices-demo/models/aegis_models), and the dashboard surfaces those live model outputs through the `Solar System`, `Infrastructure`, `Model Insights`, and `System Logs` pages.

## Table of Contents

- [What This Project Is](#what-this-project-is)
- [What Is Actually Real Today](#what-is-actually-real-today)
- [What Is Still Heuristic or Intentionally Partial](#what-is-still-heuristic-or-intentionally-partial)
- [System Goals](#system-goals)
- [High-Level Architecture](#high-level-architecture)
- [The End-to-End Intelligence Pipeline](#the-end-to-end-intelligence-pipeline)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Backend Breakdown](#backend-breakdown)
- [Model Integration](#model-integration)
- [Remediation and Containment](#remediation-and-containment)
- [Incident Memory and Persistence](#incident-memory-and-persistence)
- [Frontend Breakdown](#frontend-breakdown)
- [Observability Stack](#observability-stack)
- [Beginner Localhost Startup Guide](#beginner-localhost-startup-guide)
- [Google Login and Public Access](#google-login-and-public-access)
- [Deployment Paths](#deployment-paths)
- [Configuration](#configuration)
- [Security Model](#security-model)
- [API Surface](#api-surface)
- [Testing and Validation](#testing-and-validation)
- [Operational Proving](#operational-proving)
- [Known Limitations and Honest Status](#known-limitations-and-honest-status)
- [Related Documentation](#related-documentation)

## What This Project Is

AEGIS is trying to behave like an operator-facing resilience layer for a microservices application:

1. It ingests runtime, log, and trace-adjacent signals from the running system.
2. It keeps per-service sliding windows of recent behavior.
3. It transforms those windows into model features.
4. It scores services with a trained Isolation Forest and a trained PyTorch LSTM.
5. It classifies anomalies and raises pre-failure alerts when the LSTM sees trouble forming.
6. It runs heuristic root-cause analysis and recommendation generation.
7. It validates and executes remediation actions through a bounded policy engine.
8. It evaluates whether the action helped.
9. It retries, contains, isolates, reroutes, or escalates when recovery fails.
10. It stores incidents, logs, and event history so the next similar failure has memory.

The project is designed for two runtime modes:

- `Docker now`: works against the local Compose-based Online Boutique stack.
- `Kubernetes ready`: includes a real platform deployment path and a Kubernetes-aware orchestrator path, with live `kind` proving already documented.

## What Is Actually Real Today

These parts are implemented as live runtime paths in this repository:

- FastAPI backend with live ingestion and scoring
- Sliding-window telemetry collection
- Feature extraction for both UI and model inference
- Real model loading from [models/aegis_models](/Users/ishu/Hackathon/microservices-demo/models/aegis_models)
- Isolation Forest scoring
- PyTorch LSTM sequence scoring
- Predictive pre-failure alerting driven by the LSTM
- Real remediation pipeline with:
  - decision validation
  - action execution
  - post-action evaluation
  - bounded retry
  - containment and escalation
  - incident memory
- SQLite-backed persisted system events and backend logs
- Dashboard with four pages:
  - `#solar`
  - `#infra`
  - `#models`
  - `#logs`
- Local packaged deployment path for backend + dashboard
- Kubernetes manifests for the platform itself
- Real cluster proving notes for pod kill, crash loop, dependency failure, containment, and acknowledgement

## What Is Still Heuristic or Intentionally Partial

These are intentionally not model-driven today:

- Root-cause analysis
- Recommendation text

These are materially implemented but still operationally bounded:

- `reroute_service` is best-effort only and needs explicitly configured healthy alternatives
- rollback semantics are safe and conservative rather than advanced rollout rollback automation
- some Kubernetes telemetry panels depend on what the target cluster and workloads actually export

## System Goals

AEGIS is trying to solve five practical problems:

1. Detect service instability early enough to matter.
2. Predict failures before they become obvious outages when there is enough sequential evidence.
3. Take constrained, explainable actions instead of blindly restarting everything.
4. Preserve a durable incident trail for operators and later model work.
5. Present all of this in a single product surface that can be demoed, debugged, and extended.

## High-Level Architecture

At a high level, the system is layered like this:

```text
Online Boutique services
    ↓
Docker / Kubernetes runtime + observability stack
    ↓
AEGIS ingestion + feature extraction
    ↓
Isolation Forest + LSTM inference
    ↓
Heuristic root cause + recommendations
    ↓
Policy validation + remediation execution
    ↓
Evaluation + containment + escalation
    ↓
Incident memory + logs + dashboard surfaces
```

There are three main product surfaces:

- the application layer: Google Online Boutique
- the observability and platform layer: Prometheus, Loki, Promtail, Jaeger, Grafana, exporters, collector
- the AEGIS control plane: backend, remediation engine, persistent memory, dashboard

## The End-to-End Intelligence Pipeline

This repo now effectively implements the later productionized version of the originally proposed 10-stage pipeline.

### 1. Ingest

The backend continuously polls and ingests runtime and observability signals. In Docker mode, that includes container/runtime stats plus cached log inputs; in Kubernetes mode, runtime telemetry can come through Prometheus and cAdvisor-backed collection.

### 2. Feature Extraction

The backend converts recent observations into:

- service-level summaries for UI
- heuristic flags for remediation context
- model-specific features for Isolation Forest and LSTM inference

This logic lives primarily in:

- [backend/anomaly_api/features.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/features.py)
- [backend/anomaly_api/model_features.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/model_features.py)

### 3. Anomaly Scoring

Two model paths run:

- Isolation Forest for point-in-time statistical deviation
- LSTM for sequence-aware risk and pre-failure prediction

The backend combines those signals into a single service-level anomaly score while also preserving the individual model outputs.

### 4. Root Cause Analysis

Root cause is still heuristic. The correlation engine walks dependency relationships and score propagation patterns to estimate:

- likely root cause service
- confidence
- failure type
- affected services
- propagation path

This lives in [backend/anomaly_api/correlation.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/correlation.py).

### 5. Recommendation

Recommendation text is also heuristic. It is designed to be operationally useful rather than model-generated.

### 6. Action Decision

Once a service crosses a remediation threshold, the system builds an incident context and validates any proposed action against policy.

This includes:

- failure type classification
- safety checks
- cooldown windows
- retry budgets
- action compatibility with the active orchestrator

### 7. Action Execution

The remediation engine executes through orchestrator adapters. Today that means:

- Docker-backed execution for local runtime
- Kubernetes-aware execution for workload recovery and proving scenarios

### 8. Post-Action Evaluation

After an action, the backend evaluates whether:

- service health improved
- readiness recovered
- anomaly pressure dropped
- blast radius shrank

### 9. Retry and Containment

If the first action fails, AEGIS can:

- retry within bounded policy rules
- isolate
- attempt reroute when supported
- escalate and require manual ownership

### 10. Memory Update

All of this is persisted into SQLite-backed stores so:

- incidents can be recalled later
- event timelines can be replayed
- reports can be exported
- future repeated failures have context

## Technology Stack

### Application Layer

- Google Online Boutique microservices
- Polyglot services in Go, C#, Node.js, Python, and Java under [src](/Users/ishu/Hackathon/microservices-demo/src)

### Backend / Control Plane

- Python
- FastAPI
- Pydantic
- Uvicorn
- SQLite
- Docker SDK / Docker-aware runtime integration
- Kubernetes-aware orchestration path

### Machine Learning Runtime

- scikit-learn artifact loading for Isolation Forest
- PyTorch for LSTM inference
- NumPy-style sequence and feature construction

### Frontend

- React 18
- Vite
- D3
- plain React component styling with the project’s editorial theme system
- ESLint
- Vitest

### Observability / Platform

- Prometheus
- Loki
- Promtail
- Grafana
- Jaeger
- OpenTelemetry Collector
- kube-state-metrics
- node-exporter
- cAdvisor
- redis-exporter

### Deployment / Packaging

- Docker
- Docker Compose
- Kubernetes
- `kustomize` overlays
- `kind`
- Ingress-NGINX-style ingress deployment path
- CI via GitHub Actions

## Repository Structure

Top-level layout:

- [backend](/Users/ishu/Hackathon/microservices-demo/backend): FastAPI API, ingestion, scoring, remediation, persistence, tests
- [dashboard](/Users/ishu/Hackathon/microservices-demo/dashboard): React frontend and production dashboard container assets
- [deploy/platform](/Users/ishu/Hackathon/microservices-demo/deploy/platform): Kubernetes manifests for AEGIS itself
- [docs](/Users/ishu/Hackathon/microservices-demo/docs): deployment, telemetry, audit, and proving documentation
- [infra](/Users/ishu/Hackathon/microservices-demo/infra): helper scripts for local and Kubernetes workflows
- [ml](/Users/ishu/Hackathon/microservices-demo/ml): model loading code and training-side assets
- [models/aegis_models](/Users/ishu/Hackathon/microservices-demo/models/aegis_models): runtime artifacts actually used by the backend
- [observability](/Users/ishu/Hackathon/microservices-demo/observability): local observability config
- [pipeline](/Users/ishu/Hackathon/microservices-demo/pipeline): dataset collection and training preparation scripts
- [release](/Users/ishu/Hackathon/microservices-demo/release): Online Boutique Kubernetes manifests
- [src](/Users/ishu/Hackathon/microservices-demo/src): original boutique service source

## Backend Breakdown

The backend is centered on [backend/anomaly_api/main.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/main.py).

### Core responsibilities

- boot the API
- load required model artifacts
- initialize system persistence
- run the background score-update loop
- publish topology, infrastructure, model, event, log, and incident endpoints
- coordinate remediation and predictive alert flows

### Important backend modules

- [backend/anomaly_api/ingestion.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/ingestion.py)
  - runtime telemetry collection
  - log and trace reachability checks
  - Docker and Kubernetes telemetry pathways
- [backend/anomaly_api/features.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/features.py)
  - per-window feature extraction
- [backend/anomaly_api/model_features.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/model_features.py)
  - canonical live feature contract for IF and LSTM
- [backend/anomaly_api/correlation.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/correlation.py)
  - heuristic root-cause inference
- [backend/anomaly_api/infrastructure.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/infrastructure.py)
  - aggregated infrastructure payload builder
- [backend/anomaly_api/settings.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/settings.py)
  - environment-driven configuration
- [backend/anomaly_api/security.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/security.py)
  - operator token checks
- [backend/anomaly_api/system_store.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/system_store.py)
  - SQLite-backed event/log storage and report generation

## Model Integration

Runtime model artifacts live in [models/aegis_models](/Users/ishu/Hackathon/microservices-demo/models/aegis_models):

- `if_model.pkl`
- `scaler.pkl`
- `lstm_model.pth`

The backend expects those artifacts to exist. In production mode it fails closed rather than silently swapping in demo behavior.

### Runtime feature contract

Current live model contract:

- LSTM input: `8 x 33` timestep features
- Isolation Forest input: `66` features built from interleaved sequence statistics

The canonical feature builder is [backend/anomaly_api/model_features.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/model_features.py).

### What the dashboard exposes

The `Model Insights` page shows:

- model registry and artifact metadata
- service-level IF/LSTM scores
- score trajectories from stored history
- predictive alert stream
- dominant IF contributors
- latest sequence feature highlights

## Remediation and Containment

The remediation subsystem lives under [backend/remediation](/Users/ishu/Hackathon/microservices-demo/backend/remediation).

Key modules:

- [backend/remediation/engine.py](/Users/ishu/Hackathon/microservices-demo/backend/remediation/engine.py)
- [backend/remediation/policy.py](/Users/ishu/Hackathon/microservices-demo/backend/remediation/policy.py)
- [backend/remediation/orchestrator.py](/Users/ishu/Hackathon/microservices-demo/backend/remediation/orchestrator.py)
- [backend/remediation/action_executor.py](/Users/ishu/Hackathon/microservices-demo/backend/remediation/action_executor.py)
- [backend/remediation/evaluator.py](/Users/ishu/Hackathon/microservices-demo/backend/remediation/evaluator.py)
- [backend/remediation/containment.py](/Users/ishu/Hackathon/microservices-demo/backend/remediation/containment.py)
- [backend/remediation/memory.py](/Users/ishu/Hackathon/microservices-demo/backend/remediation/memory.py)
- [backend/remediation/models.py](/Users/ishu/Hackathon/microservices-demo/backend/remediation/models.py)

### What it does

- accepts a remediation request or runtime-triggered incident
- validates action proposals against policy
- chooses safe actions for the active runtime
- enforces cooldowns and lock windows
- executes restart / containment workflows
- evaluates post-action health
- escalates when automation should stop
- preserves incidents for later recall

### Failure patterns this repo is designed to handle

- unhealthy or disappeared workloads
- restart loops
- memory pressure and OOM-style failure patterns
- CPU saturation patterns
- dependency failure, especially shared dependencies like `redis-cart`
- log or exception storms
- multi-service propagation

## Incident Memory and Persistence

AEGIS uses SQLite for two persistence concerns:

1. system events and backend logs
2. incident memory and remediation history

Relevant runtime DB paths currently include:

- [backend/.runtime/aegis_system.db](/Users/ishu/Hackathon/microservices-demo/backend/.runtime/aegis_system.db)
- [backend/.runtime/incident_memory.db](/Users/ishu/Hackathon/microservices-demo/backend/.runtime/incident_memory.db)

What is persisted:

- structured events
- backend log lines
- remediation incident records
- similar incident recall metadata
- downloadable incident/log reports

## Frontend Breakdown

The frontend is a React/Vite application under [dashboard](/Users/ishu/Hackathon/microservices-demo/dashboard).

### Pages

- `#solar`
  - live service topology
  - orbit-based service map
  - right-side operator rail
  - service detail drilldown
- `#infra`
  - cluster/workload health
  - observability stack status
  - incidents, memory, operator context
- `#models`
  - model telemetry and feature interpretation
- `#logs`
  - live event flow
  - backend log stream
  - recovery stories
  - downloadable report generation

### Frontend tooling

- dev server: `npm run dev`
- lint: `npm run lint`
- test: `npm test`
- build: `npm run build`

## Observability Stack

### Local observability path

The Compose stack and [observability](/Users/ishu/Hackathon/microservices-demo/observability) config provide:

- Prometheus
- Loki
- Promtail
- Grafana
- Jaeger

### Kubernetes-ready platform observability

The platform manifests under [deploy/platform](/Users/ishu/Hackathon/microservices-demo/deploy/platform) include:

- backend and RBAC
- dashboard
- ingress
- Prometheus
- Loki
- Promtail
- Grafana
- Jaeger
- OTEL collector
- kube-state-metrics
- node-exporter
- cAdvisor
- redis-exporter

The repo does not fabricate missing telemetry. If a signal source is unavailable, the backend and UI should report that honestly.

## Beginner Localhost Startup Guide

If you are opening this repo for the first time and just want to run AEGIS on your laptop, use this section.

### What you are starting

You are starting two layers:

1. The application and observability stack in Docker:
   - Online Boutique microservices
   - Redis
   - Prometheus
   - Loki
   - Promtail
   - Jaeger
   - Grafana
2. The AEGIS control plane locally:
   - FastAPI backend on port `8001`
   - React dashboard on port `5173`

### Prerequisites

Make sure these are installed before you start:

- Docker Desktop
- Python 3
- Node.js and npm

Optional but useful:

- `jq` for checking JSON endpoints in the terminal

### Step 1: Open the repo

```bash
cd /Users/ishu/Hackathon/microservices-demo
```

### Step 2: Start the application and observability stack

This starts the boutique services plus Prometheus, Loki, Promtail, Jaeger, and Grafana.

```bash
docker compose up -d
```

You can confirm the containers are up with:

```bash
docker compose ps
```

### Step 3: Start the AEGIS backend and dashboard

This starts:

- backend: `http://localhost:8001`
- dashboard: `http://localhost:5173`

```bash
bash infra/start_platform.sh
```

### Step 4: Open the product

Open these in your browser:

- Storefront: `http://localhost:8080`
- AEGIS dashboard: `http://localhost:5173`
- Backend API docs: `http://localhost:8001/docs`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Jaeger: `http://localhost:16686`

### Step 5: Verify that everything is alive

In a terminal, run:

```bash
curl http://localhost:8001/health
curl http://localhost:8001/infrastructure
curl http://localhost:8001/ml/insights
```

What you should expect:

- `/health` returns `status: ok`
- `/infrastructure` returns real workload data
- `/ml/insights` may start with low or zero `ready_service_count` right after boot, then fill in as the LSTM sequence window warms up

### Step 6: Generate live traffic

The load generator usually creates traffic automatically, but you can also open the storefront and browse around to help the model windows fill faster.

### Step 7: Run the autonomous demo

From the dashboard, click `RUN DEMO`.

What should happen:

- AEGIS intentionally disrupts `recommendationservice`
- the system detects the runtime degradation
- remediation runs automatically
- the timeline, logs, and report update live
- the system restores the service and stores the report for download

### If the dashboard says `Backend offline`

Run this exact recovery sequence:

```bash
bash infra/stop_platform.sh
bash infra/start_platform.sh
```

Then refresh `http://localhost:5173`.

If you still want to verify manually:

```bash
curl http://localhost:8001/health
lsof -iTCP:8001 -sTCP:LISTEN -n -P
lsof -iTCP:5173 -sTCP:LISTEN -n -P
```

### If Model Insights looks empty just after startup

That is usually normal for the first short window after boot.

The LSTM needs live sequential data before it can move services from warm-up into `ready`. Give it a little time, keep the system running, and generate some traffic in the storefront.

### How to stop everything

Stop the AEGIS backend and dashboard:

```bash
bash infra/stop_platform.sh
```

Stop the Docker services:

```bash
docker compose down
```

If you want to remove volumes too:

```bash
docker compose down -v
```

## Google Login and Public Access

AEGIS now supports browser sign-in with Google Identity Services.

What it does:

- every Google user can sign in and view the dashboard
- user profile details are stored in the backend SQLite system store
- session state is persisted with an HTTP-only cookie
- operator actions can be restricted to configured Google emails through `AEGIS_OPERATOR_EMAILS`

What you need to configure:

- `AEGIS_GOOGLE_OAUTH_ENABLED=true`
- `AEGIS_GOOGLE_CLIENT_ID=...apps.googleusercontent.com`
- `AEGIS_SESSION_COOKIE_SECURE=true` when serving over HTTPS
- `AEGIS_OPERATOR_EMAILS=you@example.com` if you want only certain users to run demo/remediation actions

For public hosting from this machine, the important detail is that Google validates the browser origin. If you publish the dashboard at a new ngrok URL every run, you must update the Google OAuth client's **Authorized JavaScript origins** every time unless you reserve a stable ngrok domain.

## Deployment Paths

### 1. Local development

Start the application and local observability stack:

```bash
docker compose up -d
```

Start the AEGIS control plane in development mode:

```bash
bash infra/start_platform.sh
```

This path uses:

- local Python FastAPI process
- Vite dev server
- real runtime model artifacts

### 2. Local production-style Compose validation

```bash
docker compose up -d
docker compose -f docker-compose.yml -f docker-compose.platform.yml up -d --build
```

Expected endpoints:

- backend: `http://localhost:8001`
- dashboard: `http://localhost:8088`

To run this path with Google sign-in enabled, create a public env file from [.env.public.example](/Users/ishu/Hackathon/microservices-demo/.env.public.example) and use:

```bash
docker compose --env-file .env.public -f docker-compose.platform.yml up -d --build
```

### 3. Kubernetes (`kind` first)

Bootstrap cluster and ingress:

```bash
bash infra/k8s/bootstrap-kind.sh
```

Build and load images:

```bash
bash infra/k8s/build-kind-images.sh
```

Deploy the application layer:

```bash
kubectl apply -f release/kubernetes-manifests.yaml
```

Deploy the platform:

```bash
bash infra/k8s/deploy-kind.sh
```

More detail: [docs/DEPLOYMENT.md](/Users/ishu/Hackathon/microservices-demo/docs/DEPLOYMENT.md)

### 4. Public website from this PC

The supported public path is:

1. run the app + observability stack locally with Docker
2. run the AEGIS backend + dashboard locally with `docker-compose.platform.yml`
3. expose only the dashboard with ngrok
4. keep the backend private behind the dashboard reverse proxy

Full guide: [Public Hosting From Your Own PC](/Users/ishu/Hackathon/microservices-demo/docs/PUBLIC_HOSTING.md)

## Configuration

Environment variables are defined in [.env.example](/Users/ishu/Hackathon/microservices-demo/.env.example).

Key variables:

- `AEGIS_RUNTIME_MODE`
- `AEGIS_ENVIRONMENT`
- `AEGIS_CLUSTER_NAME`
- `AEGIS_ALLOWED_ORIGINS`
- `AEGIS_AUTH_ENABLED`
- `AEGIS_API_TOKEN`
- `AEGIS_GOOGLE_OAUTH_ENABLED`
- `AEGIS_GOOGLE_CLIENT_ID`
- `AEGIS_SESSION_COOKIE_NAME`
- `AEGIS_SESSION_COOKIE_SECURE`
- `AEGIS_SESSION_TTL_SECONDS`
- `AEGIS_OPERATOR_EMAILS`
- `AEGIS_ORCHESTRATOR`
- `AEGIS_K8S_NAMESPACE`
- `AEGIS_PROMETHEUS_URL`
- `AEGIS_LOKI_URL`
- `AEGIS_PROMTAIL_URL`
- `AEGIS_JAEGER_URL`
- `AEGIS_GRAFANA_URL`
- `AEGIS_OTEL_COLLECTOR_URL`
- `AEGIS_MODEL_DIR`
- `AEGIS_SYSTEM_DB`
- `AEGIS_REMEDIATION_COOLDOWN_S`
- `AEGIS_REMEDIATION_LOCK_TIMEOUT_S`
- `AEGIS_INCIDENT_MEMORY_LIMIT`
- `AEGIS_INCIDENT_MEMORY_RETENTION_DAYS`
- `AEGIS_PREDICTIVE_ALERT_THRESHOLD`
- `AEGIS_PREDICTIVE_AUTO_ACTION_THRESHOLD`
- `AEGIS_PREDICTIVE_ACTION_COOLDOWN_S`

## Security Model

Current security posture:

- mutating operator endpoints require `X-Aegis-Token` when auth is enabled
- optional Google browser sign-in gates dashboard/API access for viewers
- signed-in users are stored in SQLite with persisted session records
- operator privileges can be limited to specific Google emails with `AEGIS_OPERATOR_EMAILS`
- CORS is controlled by configured allowed origins
- the packaged dashboard talks to the backend through `/api`
- the packaged dashboard can inject operator auth at the proxy layer
- Kubernetes dashboard ingress is protected with basic auth by default
- placeholder secrets in the repo must be rotated for any serious environment

This is a practical production-hardening baseline, not full enterprise identity.

## API Surface

Important live endpoints:

- `GET /auth/config`
- `GET /auth/me`
- `POST /auth/google`
- `POST /auth/logout`
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
- `POST /remediate`
- `POST /decision/validate`
- `POST /incidents/{incident_id}/acknowledge`

Broadly:

- `topology` powers the solar page and service drilldown
- `infrastructure` powers the infra page
- `ml/insights` powers the model page
- `events`, `logs`, and `logs/report` power the logs page and report exports

## Testing and Validation

### Backend

Current backend test files include:

- [backend/tests/test_engine.py](/Users/ishu/Hackathon/microservices-demo/backend/tests/test_engine.py)
- [backend/tests/test_infrastructure.py](/Users/ishu/Hackathon/microservices-demo/backend/tests/test_infrastructure.py)
- [backend/tests/test_main_runtime.py](/Users/ishu/Hackathon/microservices-demo/backend/tests/test_main_runtime.py)
- [backend/tests/test_memory.py](/Users/ishu/Hackathon/microservices-demo/backend/tests/test_memory.py)
- [backend/tests/test_model_features.py](/Users/ishu/Hackathon/microservices-demo/backend/tests/test_model_features.py)
- [backend/tests/test_model_runtime.py](/Users/ishu/Hackathon/microservices-demo/backend/tests/test_model_runtime.py)
- [backend/tests/test_policy.py](/Users/ishu/Hackathon/microservices-demo/backend/tests/test_policy.py)
- [backend/tests/test_settings.py](/Users/ishu/Hackathon/microservices-demo/backend/tests/test_settings.py)
- [backend/tests/test_system_store.py](/Users/ishu/Hackathon/microservices-demo/backend/tests/test_system_store.py)

Typical backend validation:

```bash
python3 -m unittest discover -s backend/tests -p 'test_*.py'
python3 -m py_compile backend/anomaly_api/*.py backend/remediation/*.py
```

### Frontend

```bash
cd dashboard
npm run lint
npm test
npm run build
```

### Kubernetes manifests

The repo also validates manifest rendering for `kind` and production overlays.

## Operational Proving

The non-ML runtime path has a documented live `kind` proving pass in [docs/KIND_PROVING.md](/Users/ishu/Hackathon/microservices-demo/docs/KIND_PROVING.md).

Validated scenarios include:

- pod kill and controller recovery
- persistent crash and containment
- Redis dependency break
- operator acknowledgement flow

That proving work also tightened several runtime behaviors:

- cold telemetry does not create fake model confidence
- generic predictive spikes do not automatically self-remediate
- runtime degradation and recovery are persisted as first-class events
- dependency-aware decisions survive memory lookup rather than being overwritten incorrectly

## Known Limitations and Honest Status

This repo is strong as a working prototype and increasingly production-oriented, but it is important to be explicit about what that means.

### Strong today

- real runtime model loading
- real backend ingestion and scoring path
- real dashboard integration
- real remediation workflow
- real persistent incident and log storage
- real Kubernetes packaging and documented cluster proving

### Still not the same as “finished production software”

- root-cause analysis is still heuristic
- recommendation text is still heuristic
- reroute behavior is still limited by explicit healthy alternatives
- some telemetry quality depends on what the target application actually exports
- enterprise auth/SSO and advanced rollback semantics are not present
- cluster-specific operational quality still needs environment-by-environment validation

### Most honest summary

This is not a toy demo anymore, but it is also not pretending to be a fully finished enterprise platform. It is a real, integrated prototype with production-shaped deployment and remediation architecture, live model inference, and a documented proving path.

## Related Documentation

- [Deployment Guide](/Users/ishu/Hackathon/microservices-demo/docs/DEPLOYMENT.md)
- [Public Hosting From Your Own PC](/Users/ishu/Hackathon/microservices-demo/docs/PUBLIC_HOSTING.md)
- [Telemetry Coverage](/Users/ishu/Hackathon/microservices-demo/docs/TELEMETRY.md)
- [Production Audit](/Users/ishu/Hackathon/microservices-demo/docs/PRODUCTION_AUDIT.md)
- [KIND Operational Proving](/Users/ishu/Hackathon/microservices-demo/docs/KIND_PROVING.md)
