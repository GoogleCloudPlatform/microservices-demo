# Production Audit (Excluding ML)

## What is production-oriented now
- Packaged backend and dashboard images
- Compose production-style deployment path
- Kubernetes platform manifests with `kustomize` overlays
- Restricted CORS and token-protected mutating endpoints
- Production fail-closed mode for missing models
- Kubernetes-aware remediation adapter
- Cooldown and lease guards for automated actions
- Retention-limited incident memory with schema versioning and export path
- Aggregated infrastructure API contract
- Kubernetes platform manifests for ingress, backend, dashboard, Prometheus, Loki, Promtail, Grafana, Jaeger, OTEL collector, and exporters
- CI for backend, frontend, image builds, and manifest rendering

## What is still intentionally partial
- Full ML quality and dataset readiness
- Full mesh-first / Istio-first routing
- Enterprise identity and SSO
- Rich rollback semantics beyond safe restart/scale/contain patterns
- End-to-end live `kind` validation in this environment when `kind` is not installed locally
- Local Docker image verification may still depend on the host daemon successfully resolving upstream base-image metadata

## Current truth
- The repo is significantly closer to a production deployment shape than before, but it still depends on real model artifacts and cluster telemetry availability to reach full operational value.
- Kubernetes support is no longer only a stub, but its quality should be validated on a real cluster before calling it “done”.
