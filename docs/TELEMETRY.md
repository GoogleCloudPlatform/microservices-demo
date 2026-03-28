# Telemetry Coverage

## Live today
- Docker/container runtime stats via the backend ingestion loop
- Loki-backed log sampling and error/warning extraction
- Jaeger reachability checks
- Prometheus target health checks
- Incident and remediation state from the AEGIS backend
- SQLite-backed incident memory

## Kubernetes-ready telemetry in this repo
- OpenTelemetry Collector deployment and metrics endpoint
- Prometheus deployment and scrape configuration
- Loki, Promtail, and Grafana deployments with datasource provisioning
- kube-state-metrics
- node-exporter
- cadvisor
- redis-exporter

## Important reality check
- The repo now has a Kubernetes packaging path for platform telemetry, but app-level OpenTelemetry metrics still depend on the boutique workloads exporting to the collector.
- Some upstream boutique services have incomplete OTEL implementations, especially for metrics and traces.
- Grafana, Loki, and Promtail are now part of the platform manifests, but their operational quality still depends on cluster validation and log path compatibility in the target environment.
- The infrastructure API never fabricates missing telemetry; unavailable sections are returned as unavailable and the UI should render them explicitly.
