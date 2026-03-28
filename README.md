# AEGIS: Observability and Self-Healing Platform

AEGIS is a control plane built on top of Google Online Boutique. It ingests runtime stats and logs, computes anomaly signals, infers likely root cause, and executes remediation workflows with retry, containment, and incident memory. The ML layer is part of the repo, but the platform is designed to run cleanly without pretending trained models exist in production.

## What Is In This Repo

- `src/`: upstream Online Boutique service source
- `docker-compose.yml`: boutique app plus local observability stack
- `docker-compose.platform.yml`: packaged AEGIS backend + dashboard services for local production-style validation
- `backend/`: FastAPI API, ingestion, correlation, remediation engine, incident memory
- `dashboard/`: React dashboard
- `deploy/platform/`: Kubernetes manifests and `kustomize` overlays for the AEGIS platform
- `observability/`: local Prometheus, Loki, Promtail, Grafana config
- `pipeline/` and `ml/`: data collection, training, and inference artifacts

## Current Stack

| Layer | Technology |
|---|---|
| Application | Google Online Boutique |
| Backend API | FastAPI |
| Frontend | React + Vite |
| Metrics | Prometheus |
| Logs | Loki + Promtail |
| Traces | Jaeger |
| Collector | OpenTelemetry Collector |
| Cluster Telemetry | kube-state-metrics + node-exporter + cadvisor + redis-exporter |
| Remediation | Docker SDK + Kubernetes client |
| Memory | SQLite |
| Kubernetes Packaging | Kustomize overlays |

## Run Paths

### Local dev
```bash
docker compose up -d
bash infra/start_platform.sh
```

### Local production-style packaging
```bash
docker compose up -d
bash infra/compose-up.sh
```

### Kubernetes (`kind` first)
```bash
bash infra/k8s/bootstrap-kind.sh
bash infra/k8s/build-kind-images.sh
kubectl apply -f release/kubernetes-manifests.yaml
bash infra/k8s/deploy-kind.sh
```

## Important Reality Notes

- Production mode is fail-closed for missing models when `AEGIS_ALLOW_DEMO_MODE=false`.
- The dashboard talks to the backend through `/api`; it should not depend on hardcoded localhost URLs in production.
- Kubernetes support now includes real manifests for backend, dashboard, Prometheus, Loki, Promtail, Grafana, Jaeger, OTEL collector, and exporters, plus a remediation adapter with workload actions.
- The dashboard ingress is protected with basic auth by default in the base manifests. Rotate the checked-in placeholder secret before any real deployment.
- Some infrastructure sections intentionally report unavailable telemetry when the backing system is not deployed. The platform does not fabricate missing signals.

## Docs

- [Deployment Guide](/Users/ishu/Hackathon/microservices-demo/docs/DEPLOYMENT.md)
- [Telemetry Coverage](/Users/ishu/Hackathon/microservices-demo/docs/TELEMETRY.md)
- [Production Audit](/Users/ishu/Hackathon/microservices-demo/docs/PRODUCTION_AUDIT.md)
