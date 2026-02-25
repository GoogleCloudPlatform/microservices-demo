# GitHub Actions Workflows

This page describes the CI/CD workflows for the **Online Boutique** microservices demo app.

## Overview

Each of the 10 microservices has its own dedicated CI workflow. Workflows are triggered automatically on pushes to `main`, `staging`, and `release/**` branches, as well as on Pull Requests — but only when files in the relevant service directory are changed (path-based filtering).

Every workflow consists of two jobs:

1. **Lint & Test** — runs on every push and PR
2. **Build & Push** — runs only on push events (not PRs), pushes Docker images to Google Artifact Registry

## Configuration

Before workflows can run, set the following in your GitHub repository:

**Repository Variables** (Settings → Variables → Actions):

| Variable | Example value |
|----------|--------------|
| `GAR_LOCATION` | `us-central1` |
| `GCP_PROJECT_ID` | `my-gcp-project` |
| `GAR_REPOSITORY` | `microservices-demo` |

**Repository Secret** (Settings → Secrets → Actions):

| Secret | Description |
|--------|-------------|
| `GCP_SA_KEY` | JSON key of a GCP Service Account with **Artifact Registry Writer** role |

> **Note:** Workflows will not work on forks, as GitHub secrets are not available to forked repositories.

## Workflows

### Go Services

| Workflow | Service |
|----------|---------|
| [ci-frontend.yaml](ci-frontend.yaml) | `frontend` |
| [ci-checkoutservice.yaml](ci-checkoutservice.yaml) | `checkoutservice` |
| [ci-productcatalogservice.yaml](ci-productcatalogservice.yaml) | `productcatalogservice` |
| [ci-shippingservice.yaml](ci-shippingservice.yaml) | `shippingservice` |

**Lint & Test steps:**
- `golangci-lint` (5 min timeout)
- `go vet`
- `go test` with race detection and code coverage

---

### C# Service

| Workflow | Service |
|----------|---------|
| [ci-cartservice.yaml](ci-cartservice.yaml) | `cartservice` |

**Lint & Test steps:**
- `dotnet format --verify-no-changes`
- `dotnet build --configuration Release`
- `dotnet test` with XPlat Code Coverage (OpenCover format)

---

### Node.js Services

| Workflow | Service |
|----------|---------|
| [ci-currencyservice.yaml](ci-currencyservice.yaml) | `currencyservice` |
| [ci-paymentservice.yaml](ci-paymentservice.yaml) | `paymentservice` |

**Lint & Test steps:**
- ESLint (with fallback to basic rules if no config file exists)
- `npm audit` (non-blocking, informational)
- `npm test` (gracefully skipped if no test script is defined)

---

### Python Services

| Workflow | Service |
|----------|---------|
| [ci-emailservice.yaml](ci-emailservice.yaml) | `emailservice` |
| [ci-recommendationservice.yaml](ci-recommendationservice.yaml) | `recommendationservice` |

**Lint & Test steps:**
- `flake8` — syntax errors and undefined names (blocking), style warnings (non-blocking)
- `pylint` — error-only mode
- `pytest` with coverage (skipped gracefully if no tests found)

---

### Java Service

| Workflow | Service |
|----------|---------|
| [ci-adservice.yaml](ci-adservice.yaml) | `adservice` |

**Lint & Test steps:**
- Checkstyle via Gradle (`checkstyleMain`, `checkstyleTest`) — falls back to `compileJava` if not configured
- `gradle test`
- JaCoCo coverage report

---

## Image Tagging

All Docker images are pushed to Google Artifact Registry with three tags:

```
<GAR_LOCATION>-docker.pkg.dev/<GCP_PROJECT_ID>/<GAR_REPOSITORY>/<service>:<SHA8>
<GAR_LOCATION>-docker.pkg.dev/<GCP_PROJECT_ID>/<GAR_REPOSITORY>/<service>:<branch-name>
<GAR_LOCATION>-docker.pkg.dev/<GCP_PROJECT_ID>/<GAR_REPOSITORY>/<service>:latest
```

`<SHA8>` is the first 8 characters of the commit SHA, used for precise version pinning.

## Artifacts

Test results and coverage reports are uploaded as GitHub Actions artifacts after each run and are available for download from the workflow summary page.

| Service | Artifact name |
|---------|--------------|
| Go services | `<service>-coverage` (coverage.out) |
| cartservice | `cartservice-coverage` (OpenCover XML) |
| Python services | `<service>-coverage` (coverage.xml) |
| adservice | `adservice-test-results` (HTML report + JaCoCo) |