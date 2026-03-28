# Production Audit

## What is production-oriented now
- Packaged backend and dashboard images
- Compose production-style deployment path
- Kubernetes platform manifests with `kustomize` overlays
- Restricted CORS and token-protected mutating endpoints
- Uploaded Isolation Forest and PyTorch LSTM artifacts integrated into the backend runtime
- Backend image copies the runtime model artifacts and prefers CPU-targeted PyTorch wheels
- Model insights API and dedicated frontend page
- Kubernetes-aware remediation adapter
- Cooldown and lease guards for automated actions
- Retention-limited incident memory with schema versioning and export path
- Aggregated infrastructure API contract
- Kubernetes platform manifests for ingress, backend, dashboard, Prometheus, Loki, Promtail, Grafana, Jaeger, OTEL collector, and exporters
- CI for backend, frontend, image builds, and manifest rendering

## What is still intentionally partial
- Root-cause analysis remains heuristic
- Recommendation text remains rule-based
- Full mesh-first / Istio-first routing
- Enterprise identity and SSO
- Rich rollback semantics beyond safe restart/scale/contain patterns
- End-to-end live `kind` validation in this environment when `kind` is not installed locally
- Local Docker image verification may still depend on the host daemon successfully resolving upstream base-image metadata

## Current truth
- The runtime no longer depends on synthetic scoring or demo fallback behavior.
- The uploaded model artifacts now load and score inside the backend, and the dashboard exposes those outputs through a dedicated model insights surface.
- Kubernetes support is materially stronger than before, but it still needs live cluster validation before calling the whole product fully production-ready.
