# AI Observability & Self-Healing Platform

An autonomous observability and self-healing platform built on top of a live microservices application. The system continuously collects logs, metrics, and traces from 11 running microservices, feeds them into a machine learning layer that detects anomalies in real time and predicts failures 1–5 minutes before they occur, then automatically triggers remediation playbooks via the Docker API — all surfaced on a real-time React dashboard with Claude AI-generated natural language explanations of every incident.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│               Online Boutique (11 Microservices)                │
│  frontend · cart · checkout · payment · currency · shipping     │
│  email · productcatalog · recommendation · ad · loadgenerator   │
└──────────────┬──────────────────────────────┬───────────────────┘
               │ metrics (OTLP)               │ logs (stdout)
               ▼                              ▼
┌──────────────────────────┐    ┌─────────────────────────────────┐
│  Prometheus  │  Jaeger   │    │   Loki  ◄──── Promtail          │
│  (metrics)   │  (traces) │    │   (logs)                        │
└──────────────┬───────────┘    └──────────────┬──────────────────┘
               │                               │
               └──────────────┬────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ML Layer                                 │
│                                                                 │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │   Isolation Forest      │  │       Predictive LSTM        │  │
│  │  (real-time anomaly     │  │  (failure prediction 1-5min  │  │
│  │   detection on metrics) │  │   ahead on time-series data) │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ anomaly scores + predictions
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Remediation Engine                           │
│         (Docker API · escalating playbooks · auto-heal)        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Real-Time Dashboard                           │
│   React + Tailwind · live anomaly scores · incident timeline    │
│   Claude AI incident explanations · remediation audit log       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ML Approach

### Isolation Forest — Unsupervised Anomaly Detection
Runs continuously on a sliding window of Prometheus metrics (error rates, latency percentiles, request throughput, container CPU/memory). Isolation Forest assigns an anomaly score to each service at every tick; scores above the contamination threshold trigger an alert and feed the remediation engine. No labelled training data required — it learns the "normal" baseline from live traffic.

### Predictive LSTM — Failure Prediction Before It Happens
A sequence-to-one LSTM trained on historical failure scenario data (injected fault recordings + Drain3-parsed log feature vectors + Prometheus time-series). Given the last *N* minutes of system state, it predicts the probability of a failure event occurring in the next 1–5 minutes. This allows the remediation engine to act *before* a service actually goes down rather than reacting after the fact.

---

## Stack

| Layer | Technology |
|---|---|
| **Application** | Google Online Boutique (11 microservices, Docker Compose) |
| **Metrics** | Prometheus v3.3.1 |
| **Logs** | Loki 3.7.1 + Promtail 3.6.8 |
| **Traces** | Jaeger 1.76.0 (OTLP gRPC) |
| **Dashboards** | Grafana 12.0.2 |
| **Log parsing** | Drain3 (log template mining for feature extraction) |
| **Anomaly detection** | Python · scikit-learn · Isolation Forest |
| **Failure prediction** | Python · PyTorch · LSTM |
| **Backend API** | FastAPI (anomaly + prediction API) |
| **Dashboard API** | Node.js / Express |
| **Frontend** | React + Tailwind CSS |
| **AI Explanations** | Claude API (Anthropic) |
| **Local tunnel** | ngrok |

---

## Repository Structure

```
microservices-demo/
├── src/                    # All Online Boutique microservice source code
├── docker-compose.yml      # Full stack: 11 services + observability
├── observability/          # Prometheus, Loki, Grafana, Promtail configs
│
├── pipeline/               # Data collection and preprocessing
│   ├── scripts/            # Collection, injection, feature-extraction scripts
│   ├── notebooks/          # EDA and model training notebooks
│   └── data/
│       ├── raw_logs/       # Raw log dumps (normal/ and failures/)
│       ├── processed/      # Feature matrices ready for training
│       └── models/         # Saved model weights (.pt, .pkl)
│
├── ml/
│   ├── lstm/               # LSTM model definition, training, inference
│   ├── isolation_forest/   # Isolation Forest training and scoring
│   └── shared/             # Feature engineering, data loaders, utils
│
├── backend/
│   ├── anomaly_api/        # FastAPI service: scores + predictions endpoint
│   └── remediation/        # Remediation engine + Docker API playbooks
│
├── dashboard/
│   ├── frontend/           # React + Tailwind real-time dashboard
│   └── api/                # Node.js API bridging dashboard to backend
│
└── infra/
    └── ngrok/              # ngrok tunnel config for public URL exposure
```

---

## How to Run

### Prerequisites
- Docker 20+ and Docker Compose 2.0+
- Python 3.9+
- Node.js 18+
- ngrok account + auth token
- Anthropic API key

### Start the Full Observability Stack

```bash
# Clone and start all 17 containers
git clone https://github.com/ishitac1205/microservices-demo
cd microservices-demo
docker compose up -d

# Verify all containers are running
docker compose ps
```

### Access the UIs

| Service | URL |
|---|---|
| Online Boutique | http://localhost:8080 |
| Grafana | http://localhost:3000 (admin / admin) |
| Prometheus | http://localhost:9090 |
| Jaeger Traces | http://localhost:16686 |
| Loki | http://localhost:3100 |

### ML Pipeline, Backend, and Dashboard
> Setup instructions for the ML pipeline, backend API, and dashboard will be added as each component is built.

---

## Team

[Team Member Names]

---

## Hackathon

Built for [Hackathon Name] — 36 hours
