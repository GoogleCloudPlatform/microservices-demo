# Observability: Prometheus + Grafana

This document describes the design and implementation plan for adding Prometheus and Grafana observability to Online Boutique, using the existing OpenTelemetry instrumentation as the data source.

## Goals

- Collect RED metrics (Rate, Errors, Duration) for all OTel-instrumented services
- Deploy Prometheus and Grafana inside the cluster with no external dependencies
- Remain compatible with the existing `google-cloud-operations` component (both can run simultaneously)
- Follow the existing kustomize component pattern so the stack is opt-in

## Non-goals

- Replacing or modifying per-service OTel code
- Adding OTel to uninstrumented services (cartservice, adservice, shoppingassistantservice) — that is a separate effort
- Production hardening (persistent storage, HA, auth) — this targets dev/staging clusters

## Services in scope

These 7 services already emit OTLP traces and will feed the pipeline:

| Service | Language |
|---|---|
| frontend | Go |
| checkoutservice | Go |
| productcatalogservice | Go |
| paymentservice | Node.js |
| currencyservice | Node.js |
| emailservice | Python |
| recommendationservice | Python |

`shippingservice` is currently out of scope because tracing is still a stub (see issue #422).

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Microservices (OTel-instrumented)                           │
│  frontend, checkoutservice, productcatalogservice,           │
│  paymentservice, currencyservice, emailservice,              │
│  recommendationservice                                        │
└──────────────────────┬───────────────────────────────────────┘
                       │ OTLP gRPC :4317
                       ▼
          ┌────────────────────────┐
          │   OTel Collector       │  (new deployment in this component)
          │   otel-collector-      │
          │   prom                 │
          │                        │
          │  receivers:            │
          │    otlp (grpc :4317)   │
          │                        │
          │  connectors:           │
          │    spanmetrics         │◄─── derives RED metrics from spans
          │    connector           │
          │                        │
          │  exporters:            │
          │    prometheus (:8889)  │──► scraped by Prometheus
          └────────────────────────┘
                       │ scrape :8889/metrics
                       ▼
              ┌─────────────────┐
              │   Prometheus    │  :9090
              └────────┬────────┘
                       │ PromQL datasource
                       ▼
               ┌──────────────┐
               │   Grafana    │  :3000
               └──────────────┘
```

### Why a dedicated collector?

The existing `google-cloud-operations` component runs an OTel Collector that exports to Cloud Trace and Cloud Monitoring. Rather than patching that collector (which would couple these two concerns), this component deploys a separate collector named `otel-collector-prom` for the Prometheus/Grafana pipeline. Services can be configured to export OTLP to either collector endpoint. In the currently shipped configuration, `otel-collector-prom` also forwards traces to `opentelemetrycollector:4317`, so pointing a service at `otel-collector-prom:4317` sends telemetry into the Prometheus/Grafana pipeline while also continuing to feed the existing Google Cloud operations collector.

### spanmetricsconnector

The OTel Collector's `spanmetricsconnector` generates Prometheus metrics from trace span data:

- `calls_total{service_name, span_name, status_code}` — request rate + error rate
- `duration_milliseconds_bucket{...}` — latency histogram (for p50/p95/p99)

This requires no code changes in services and works with the current tracing-only instrumentation.

## Kustomize component

All resources live in a new kustomize component:

```
kustomize/components/prometheus-grafana/
├── kustomization.yaml          # component definition + service env patches
├── otel-collector-prom.yaml    # OTel Collector (prom-focused config)
```

Planned for future phases (not in this PR):

- `prometheus.yaml` (Phase 2)
- `grafana.yaml` (Phase 3)
- `dashboards/services-overview.json` (Phase 3)

To enable it, add to `kubernetes-manifests/kustomization.yaml`:

```yaml
components:
  - ../kustomize/components/prometheus-grafana
```

When enabled, `kustomization.yaml` patches each OTel-instrumented service to set:

```yaml
- name: COLLECTOR_SERVICE_ADDR
  value: "otel-collector-prom:4317"
- name: OTEL_SERVICE_NAME
  value: "<servicename>"
- name: ENABLE_TRACING
  value: "1"
```

> If `google-cloud-operations` is also enabled, services will have duplicate `COLLECTOR_SERVICE_ADDR` entries — the last patch wins. To fan out to both collectors simultaneously, the OTel Collector can be configured to forward to the GCP collector as an additional exporter (see Phase 5 (optional)).

## Implementation plan

### Phase 1: OTel Collector (prometheus-focused)

**Goal:** Collector receives OTLP from services, generates RED metrics, exposes `/metrics` for Prometheus.

**Steps:**

1. Create `kustomize/components/prometheus-grafana/otel-collector-prom.yaml`
   - Deployment: `otel/opentelemetry-collector-contrib:0.150.1` (match existing version)
   - ConfigMap with pipeline: `otlp receiver → spanmetricsconnector → prometheus exporter`
   - Service exposing port 4317 (OTLP) and 8889 (prometheus scrape)
   - ServiceAccount (minimal, no GCP bindings needed)

   Collector config outline:
   ```yaml
   receivers:
     otlp:
       protocols:
         grpc:
           endpoint: 0.0.0.0:4317

   connectors:
     spanmetrics:
       histogram:
         explicit:
           buckets: [5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s]
       dimensions:
         - name: http.method
         - name: http.status_code

   exporters:
     prometheus:
       endpoint: "0.0.0.0:8889"
       namespace: boutique

   service:
     pipelines:
       traces/spanmetrics:
         receivers: [otlp]
         exporters: [spanmetrics]
       metrics/prometheus:
         receivers: [spanmetrics]
         exporters: [prometheus]
   ```

2. Verify: `kubectl port-forward svc/otel-collector-prom 8889` → `curl localhost:8889/metrics` returns `boutique_calls_total` etc.

### Phase 2: Prometheus

**Goal:** Prometheus scrapes the collector and retains metrics.

**Steps:**

1. Create `kustomize/components/prometheus-grafana/prometheus.yaml`
   - ConfigMap with `prometheus.yml`:
     ```yaml
     scrape_configs:
       - job_name: otel-collector-prom
         scrape_interval: 15s
         static_configs:
           - targets: ['otel-collector-prom:8889']
     ```
   - Deployment: `prom/prometheus:v3.4.0` (or latest stable at implementation time)
   - Service on port 9090 (ClusterIP)
   - Args: `--storage.tsdb.retention.time=7d` (no PVC needed for dev)

2. Verify: `kubectl port-forward svc/prometheus 9090` → query `boutique_calls_total` returns results.

### Phase 3: Grafana

**Goal:** Grafana connects to Prometheus and shows a pre-built RED metrics dashboard.

**Steps:**

1. Create `kustomize/components/prometheus-grafana/grafana.yaml`
   - Deployment: `grafana/grafana:12.0.1` (or latest stable at implementation time)
   - Service on port 3000 (ClusterIP or LoadBalancer for easy access)
   - ConfigMap: datasource provisioning pointing to `http://prometheus:9090`
   - ConfigMap: dashboard provisioning pointing to `/etc/grafana/dashboards`

2. Create `kustomize/components/prometheus-grafana/dashboards/services-overview.json`

   Dashboard panels:
   - **Request rate** — `sum(rate(boutique_calls_total[1m])) by (service_name)` — line chart
   - **Error rate** — `sum(rate(boutique_calls_total{status_code="STATUS_CODE_ERROR"}[1m])) by (service_name)` — line chart
   - **p99 latency** — `histogram_quantile(0.99, sum(rate(boutique_duration_milliseconds_bucket[5m])) by (le, service_name))` — line chart
   - **p50 latency** — same with 0.50
   - **Calls heatmap** — `boutique_duration_milliseconds_bucket` — heatmap by service
   - Template variable: `$service` filter (multi-select from `service_name` label)

3. Verify: `kubectl port-forward svc/grafana 3000` → open browser → dashboard loads with live data after load generator runs.

### Phase 4: kustomization.yaml + service patches

**Goal:** Wire services to the new collector via kustomize patches.

**Steps:**

1. Create `kustomize/components/prometheus-grafana/kustomization.yaml`:
   ```yaml
   apiVersion: kustomize.config.k8s.io/v1alpha1
   kind: Component

   resources:
     - otel-collector-prom.yaml
     - prometheus.yaml
     - grafana.yaml

   patches:
     # one patch block per OTel-instrumented service
     - patch: |-
         apiVersion: apps/v1
         kind: Deployment
         metadata:
           name: frontend
         spec:
           template:
             spec:
               containers:
                 - name: server
                   env:
                     - name: COLLECTOR_SERVICE_ADDR
                       value: "otel-collector-prom:4317"
                     - name: OTEL_SERVICE_NAME
                       value: "frontend"
                     - name: ENABLE_TRACING
                       value: "1"
     # ... repeat for checkoutservice, productcatalogservice,
     #     paymentservice, currencyservice, emailservice, recommendationservice
   ```

2. Verify: `kubectl get deployment frontend -o json | jq '.spec.template.spec.containers[0].env'` shows the three env vars.

### Phase 5 (optional): Fan-out to both GCP and Prometheus

If both `google-cloud-operations` and `prometheus-grafana` are enabled, configure `otel-collector-prom` to forward traces upstream to the GCP collector so both pipelines receive data without services needing two addresses:

```yaml
exporters:
  otlp/gcp:
    endpoint: opentelemetrycollector:4317
    tls:
      insecure: true

service:
  pipelines:
    traces/forward:
      receivers: [otlp]
      exporters: [otlp/gcp, spanmetrics]
```

This makes the prometheus collector a transparent proxy for the GCP collector.

## Validation checklist

- [ ] `otel-collector-prom` pod is Running
- [ ] `curl otel-collector-prom:8889/metrics` returns `boutique_calls_total`
- [ ] Prometheus target `otel-collector-prom:8889` shows State=UP
- [ ] `boutique_calls_total` has data points in Prometheus after load generator runs
- [ ] Grafana datasource test passes
- [ ] "Services Overview" dashboard renders all panels
- [ ] p99 latency panel shows per-service breakdown
- [ ] `google-cloud-operations` component still works independently (if applicable)

## Resource estimates (per pod, no limits set for dev)

| Pod | CPU request | Memory request |
|---|---|---|
| otel-collector-prom | 100m | 128Mi |
| prometheus | 200m | 512Mi |
| grafana | 100m | 128Mi |

## Future work

- Add OTel instrumentation to cartservice (C#) and adservice (Java) — enables them to join this pipeline
- Add metrics instrumentation (not just tracing) to existing services for richer signal (e.g., cache hit rates, queue depths)
- Add alerting rules (PrometheusRule) for SLO breaches (e.g., p99 > 500ms, error rate > 1%)
- Persistent storage for Prometheus (PersistentVolumeClaim) for staging/long-lived environments
- Grafana authentication (currently anonymous access for dev convenience)
