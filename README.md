# AEGIS

AEGIS is an observability and automated remediation control plane built on top of Google Online Boutique. It collects live service telemetry, scores anomalies with trained models, performs heuristic root-cause analysis, executes controlled remediation actions, and records incident memory for future decisions.

This repo now runs with the uploaded trained artifacts in [models/aegis_models](/Users/ishu/Hackathon/microservices-demo/models/aegis_models). There is no demo or sinusoidal scoring path in the backend runtime anymore.

Required runtime artifacts:
- `models/aegis_models/if_model.pkl`
- `models/aegis_models/scaler.pkl`
- `models/aegis_models/lstm_model.pth`

The larger `X_*.npy` and `y_labels.npy` files are treated as local training assets and are not required for runtime packaging.

## What Is Live In This Repo

- Real telemetry ingestion from Docker stats, Loki, and Jaeger
- Real trained model loading for:
  - Isolation Forest anomaly scoring
  - PyTorch LSTM sequence prediction
- Real remediation pipeline:
  - decision validation
  - execution
  - post-action evaluation
  - retry / isolate / reroute / escalate containment
  - incident memory persistence
- Real dashboard surfaces:
  - `Solar System` service topology
  - `Infrastructure` cluster / observability / remediation page
  - `Model Insights` page for ML telemetry and feature drivers
  - `System Logs` page for persisted backend events and logs

## Deliberately Heuristic / Hardcoded

These two areas are still rule-based by design in the current product:

- Root-cause analysis
- Recommendation text

Everything else is expected to run from real inputs, real models, and real execution paths.

## Repository Layout

- [src](/Users/ishu/Hackathon/microservices-demo/src): Google Online Boutique source services
- [docker-compose.yml](/Users/ishu/Hackathon/microservices-demo/docker-compose.yml): boutique app plus local observability stack
- [docker-compose.platform.yml](/Users/ishu/Hackathon/microservices-demo/docker-compose.platform.yml): packaged AEGIS backend + dashboard
- [backend](/Users/ishu/Hackathon/microservices-demo/backend): FastAPI API, ingestion, scoring, remediation, memory
- [dashboard](/Users/ishu/Hackathon/microservices-demo/dashboard): React frontend
- [deploy/platform](/Users/ishu/Hackathon/microservices-demo/deploy/platform): Kubernetes manifests and overlays for AEGIS itself
- [models/aegis_models](/Users/ishu/Hackathon/microservices-demo/models/aegis_models): trained model artifacts currently used by the backend
- [pipeline](/Users/ishu/Hackathon/microservices-demo/pipeline): data collection, labeling, and dataset generation
- [observability](/Users/ishu/Hackathon/microservices-demo/observability): local Prometheus, Loki, Promtail, Grafana config

## Runtime Architecture

### Backend

The FastAPI service in [backend/anomaly_api/main.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/main.py):

- maintains sliding windows of live observations
- extracts rich features for UI, heuristics, and remediation context
- builds the real 33-feature LSTM sequence input from live telemetry
- derives the real 66-feature Isolation Forest input from sequence statistics
- loads the uploaded model artifacts from `models/aegis_models`
- raises LSTM-backed pre-failure alerts and can trigger preventive actions before the service crosses the main incident threshold
- persists structured events and backend logs into SQLite for timeline and log replay
- exposes:
  - `/health`
  - `/status`
  - `/topology`
  - `/infrastructure`
  - `/ml/insights`
  - `/events`
  - `/logs`
  - `/history`
  - `/window/{service}`
  - remediation and incident endpoints

### Frontend

The dashboard has four views:

- `#solar`: service topology and remediation controls
- `#infra`: infrastructure, observability, incidents, containment, and memory
- `#models`: model metadata, service-level ML states, feature drivers, and sequence highlights
- `#logs`: persisted system timeline and backend log stream

### Remediation

The remediation subsystem under [backend/remediation](/Users/ishu/Hackathon/microservices-demo/backend/remediation) implements:

- policy-driven action validation
- Docker executor today
- Kubernetes-aware executor path for deployments and pod recovery
- cooldowns and service leases
- containment and escalation
- SQLite-backed incident memory

## Model Integration

The backend uses:

- [models/aegis_models/if_model.pkl](/Users/ishu/Hackathon/microservices-demo/models/aegis_models/if_model.pkl)
- [models/aegis_models/scaler.pkl](/Users/ishu/Hackathon/microservices-demo/models/aegis_models/scaler.pkl)
- [models/aegis_models/lstm_model.pth](/Users/ishu/Hackathon/microservices-demo/models/aegis_models/lstm_model.pth)

Current live model contract:

- LSTM input: `8 x 33` timestep features
- Isolation Forest input: `66` interleaved `mean/std` features derived from the same sequence family

The canonical live feature builder is in [backend/anomaly_api/model_features.py](/Users/ishu/Hackathon/microservices-demo/backend/anomaly_api/model_features.py).

## How To Run

### Local dev

```bash
docker compose up -d
bash infra/start_platform.sh
```

This starts the boutique app and local observability stack, then runs the backend and dashboard in development mode.

### Local packaged runtime

```bash
docker compose up -d
bash infra/compose-up.sh
```

This validates the production-style backend and dashboard containers locally.

### Kubernetes (`kind` first)

```bash
bash infra/k8s/bootstrap-kind.sh
bash infra/k8s/build-kind-images.sh
kubectl apply -f release/kubernetes-manifests.yaml
bash infra/k8s/deploy-kind.sh
```

## Configuration

See [.env.example](/Users/ishu/Hackathon/microservices-demo/.env.example).

Important values:

- `AEGIS_RUNTIME_MODE`
- `AEGIS_AUTH_ENABLED`
- `AEGIS_API_TOKEN`
- `AEGIS_ALLOWED_ORIGINS`
- `AEGIS_ORCHESTRATOR`
- `AEGIS_MODEL_DIR`
- `AEGIS_PROMETHEUS_URL`
- `AEGIS_LOKI_URL`
- `AEGIS_PROMTAIL_URL`
- `AEGIS_JAEGER_URL`
- `AEGIS_GRAFANA_URL`
- `AEGIS_OTEL_COLLECTOR_URL`

## Security Notes

- Mutating endpoints require `X-Aegis-Token` when auth is enabled.
- In the packaged dashboard path, nginx injects the operator token into proxied `/api` requests so the browser does not need to embed that secret.
- The Kubernetes dashboard ingress is protected with basic auth by default.
- Rotate the checked-in placeholder secrets before any real deployment.

## Validation Status

Validated in this repo after the current integration pass:

- backend unit tests
- model artifact load and scoring tests
- frontend tests
- frontend production build
- Python module compilation
- Kubernetes manifest rendering for `kind` and `production` overlays

Not fully validated in this local environment:

- live end-to-end `kind` deployment, because `kind` is not installed here
- a full local Docker image verification pass, because earlier host-daemon metadata resolution stalled on this machine

## Docs

- [Deployment Guide](/Users/ishu/Hackathon/microservices-demo/docs/DEPLOYMENT.md)
- [Telemetry Coverage](/Users/ishu/Hackathon/microservices-demo/docs/TELEMETRY.md)
- [Production Audit](/Users/ishu/Hackathon/microservices-demo/docs/PRODUCTION_AUDIT.md)
