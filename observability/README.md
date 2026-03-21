# Observability Platform for Online Boutique

SLO-driven observability layer for the [Google Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) microservices demo, built with Prometheus, Grafana, and Istio.

## Architecture

```
Istio Service Mesh (telemetry from 10 microservices)
    |
Prometheus (48 recording rules + 41 alert rules)
    |
Alertmanager (Slack/PagerDuty integration)
    |
Grafana (4 dashboards)
```

## What's Included

### Prometheus Recording Rules (`prometheus-rules/`)

| File | Rules | Description |
|------|-------|-------------|
| `slo-rules.yaml` | 60 | Per-service RED metrics (RPS, error rate, availability, P99/P95 latency) + 30-day error budgets |
| `platform-rules.yaml` | 6 | Platform health composite signal + PlatformDown alert |
| `slo-alerts.yaml` | 41 | Multi-window burn rate alerts + latency SLO alerts |

### Recording Rules (60 total)

| Rule | Description | Per Service |
|------|-------------|-------------|
| `slo:service_rps:rate5m` | Request rate (5m window) | x10 |
| `slo:service_error_rate:ratio5m` | 5xx error rate | x10 |
| `slo:service_availability:ratio5m` | Availability (1 - error rate) | x10 |
| `slo:service_latency_p99:seconds` | P99 latency | x10 |
| `slo:service_latency_p95:seconds` | P95 latency | x10 |
| `slo:service_error_budget_remaining:ratio` | 30-day rolling error budget | x10 |

### Alert Rules (41 total)

| Alert | Condition | Severity | Count |
|-------|-----------|----------|-------|
| PlatformDown | `platform_up == 0` for 2m | critical | 1 |
| HighErrorBurnRate | 14.4x error budget burn over 1h | critical | 10 |
| SlowErrorBurnRate | 6x error budget burn over 6h | warning | 10 |
| HighLatency | P99 > 2s for 5m | critical | 10 |
| ElevatedLatency | P95 > 1s for 10m | warning | 10 |

### Grafana Dashboards (`grafana-dashboards/`)

| Dashboard | Description |
|-----------|-------------|
| Platform Health | UP/DOWN status, Gateway vs App traffic, Health Factors (PASS/FAIL) |
| SLO Overview | Error budgets, availability table, P99/P95 latency, traffic per service |
| Service RED Metrics | Per-service drill-down: RPS, errors, latency (P50/P95/P99), pod health |

### Services Monitored (10 microservices)

| Service | Language | Description |
|---------|----------|-------------|
| frontend | Go | Web frontend |
| cartservice | C# | Shopping cart |
| checkoutservice | Go | Checkout flow |
| productcatalogservice | Go | Product catalog |
| currencyservice | Node.js | Currency conversion |
| paymentservice | Node.js | Payment processing |
| shippingservice | Go | Shipping quotes |
| emailservice | Python | Email confirmation |
| recommendationservice | Python | Product recommendations |
| adservice | Java | Ad serving |

## Prerequisites

- Kubernetes cluster (EKS, GKE, Kind, or Minikube)
- Istio service mesh installed
- Helm 3.x

## Quick Start

### 1. Deploy Online Boutique with Istio

```bash
# Install Istio
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled

# Deploy Online Boutique
kubectl apply -f ./kubernetes-manifests/
```

### 2. Install kube-prometheus-stack

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.enabled=true \
  --set grafana.adminPassword=admin
```

### 3. Apply Prometheus Rules

```bash
kubectl apply -f observability/prometheus-rules/
```

### 4. Import Grafana Dashboards

```bash
kubectl apply -f observability/grafana-dashboards/
```

### 5. Generate Traffic (load generator is included)

The `loadgenerator` service is part of Online Boutique and will automatically generate traffic to the frontend.

### 6. Access Grafana

```bash
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80
```

Open http://localhost:3000 (admin/admin)

## SLO Framework

### Target: 99.9% availability (error budget = 0.1%)

The SLO framework follows the Google SRE model:

1. **SLIs** (Service Level Indicators) - measured via Istio telemetry
2. **SLOs** (Service Level Objectives) - 99.9% availability target
3. **Error Budgets** - 30-day rolling window, consumed by errors
4. **Burn Rate Alerts** - multi-window alerting to detect budget consumption

### How Burn Rate Alerts Work

Instead of simple threshold alerts, burn rate alerts detect the *rate* at which error budget is being consumed:

- **Fast burn (14.4x)**: At this rate, the entire 30-day error budget would be consumed in ~2 hours. Fires after 2 minutes of sustained burn. This catches severe incidents.
- **Slow burn (6x)**: At this rate, the budget would be consumed in ~5 days. Fires after 15 minutes. This catches gradual degradation before it becomes critical.

## Troubleshooting Scenarios

| Scenario | Dashboard | What to Check |
|----------|-----------|---------------|
| Is the platform down? | Platform Health | UP/DOWN status + Health Factors |
| Which service is failing? | SLO Overview | Availability table (sorted worst-first) |
| Is it slow? | SLO Overview | P99/P95 latency panels |
| Why did we get paged? | Alert Rules | Which alert is firing + service label |
| Should we release today? | SLO Overview | Error budget remaining per service |
| Is traffic normal? | Platform Health | Gateway vs App Traffic comparison |

## License

This observability layer is open source. The Online Boutique application is maintained by Google Cloud Platform.
