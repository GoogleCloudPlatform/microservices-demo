# Running Online Boutique — Three Methods

This is a microservices demo with 11 services (Go, .NET, Node, Python, Java) plus Redis. Below is what's required to run it three ways: Kubernetes, Docker Compose, or natively. Tested on macOS (Apple Silicon) on 2026-05-04.

| | Kubernetes | Docker Compose | Native |
|---|---|---|---|
| **Isolation** | Full | Per-container | None |
| **Setup time** | ~25 min (first build) | ~25 min (first build) | ~30 min (first build) |
| **Disk** | ~10 GB | ~10 GB | ~5 GB |
| **RAM at idle** | ~3–6 GB | ~2–3 GB | ~1.5 GB |
| **Officially supported** | Yes | No (no compose file shipped) | No |

---

## Method 1 — Kubernetes (upstream-supported)

### Required software

| Tool | Version | Purpose |
|---|---|---|
| Docker | any modern | Image builds + container runtime |
| kubectl | any | Cluster control |
| Local k8s cluster | one of OrbStack k8s / Docker Desktop k8s / minikube / kind | The cluster |
| skaffold | ≥ 2.0.2 | Builds all 11 images and applies manifests |

### Steps (OrbStack)

```sh
orbctl start k8s
brew install skaffold
skaffold config set --kube-context orbstack local-cluster true   # tells skaffold not to push to a registry
skaffold run                                                      # ~20 min first time
kubectl port-forward deployment/frontend 8080:8080
```

Open http://localhost:8080.

### Gotchas

- **OrbStack isn't auto-detected by skaffold** as a local cluster — without `local-cluster true` it fails with "No push access to specified image repository." Docker Desktop / minikube / kind are auto-detected.
- **cartservice TARGETARCH bug.** The .NET image's Dockerfile uses `ARG TARGETARCH=amd64` and expects buildx to inject `arm64`. With skaffold's docker driver this isn't propagated, so on Apple Silicon the produced binary is x86_64 and crash-loops with `Dynamic loader not found: /lib64/ld-linux-x86-64.so.2`. Workaround: rebuild manually and re-point the deployment:
  ```sh
  cd src/cartservice/src
  docker build --platform linux/arm64 --build-arg TARGETARCH=arm64 -t cartservice:<git-sha> .
  kubectl set image deployment/cartservice server=cartservice:<git-sha>
  ```
- **Multi-arch builds are slow.** Default `skaffold.yaml` builds `linux/amd64,linux/arm64`. For local-only testing, narrowing to one platform halves build time.

### Cleanup

```sh
skaffold delete         # removes deployments
orbctl stop k8s         # stops the cluster (note: this restarts Docker, killing any compose stack too)
```

---

## Method 2 — Docker Compose (no k8s)

The repo doesn't ship a `docker-compose.yml`, but every service has a Dockerfile, so one can be authored.

### Required software

| Tool | Version | Purpose |
|---|---|---|
| Docker | any modern | Build + run |
| Docker Compose | v2 (bundled with Docker Desktop / OrbStack) | Orchestration |

That's it — no kubectl, no skaffold, no k8s cluster.

### Steps

1. Author `docker-compose.yml` at repo root wiring the 11 services + redis. Each service's env vars come from the kubernetes manifests (e.g. `kubernetes-manifests/checkoutservice.yaml`). Use service names as gRPC hostnames (Compose's DNS handles resolution). Map only the frontend's port to the host.
2. Build images (or reuse those from a prior `skaffold run`):
   ```sh
   docker compose build
   docker compose up -d
   ```
3. Open http://localhost:8080.

### Service env-var wiring (from k8s manifests)

| Service | Internal port | Notable env |
|---|---|---|
| redis-cart | 6379 | — |
| productcatalogservice | 3550 | `PORT` |
| shippingservice | 50051 | `PORT` |
| paymentservice | 50051 | `PORT` |
| currencyservice | 7000 | `PORT` |
| emailservice | 8080 | `PORT` |
| recommendationservice | 8080 | `PORT`, `PRODUCT_CATALOG_SERVICE_ADDR` |
| cartservice | 7070 | `ASPNETCORE_HTTP_PORTS=7070`, `REDIS_ADDR=redis-cart:6379` |
| adservice | 9555 | `PORT` |
| checkoutservice | 5050 | `PORT`, `*_SERVICE_ADDR` for product/shipping/payment/email/currency/cart |
| frontend | 8080 | `PORT`, `*_SERVICE_ADDR` for product/currency/cart/recommendation/shipping/checkout/ad |

Inside the Compose network there are no port conflicts because each container has its own network namespace.

### Gotchas

- **No host port conflicts** here (only the frontend is exposed on the host).
- If you reuse images from a `skaffold run`, they'll be tagged `<service>:<git-sha>`.

### Cleanup

```sh
docker compose down
```

---

## Method 3 — Native (no containers, no k8s)

### Required software

| Tool | Version | Used by |
|---|---|---|
| Go | ≥ 1.22 | frontend, productcatalogservice, shippingservice, checkoutservice |
| .NET SDK | 10.x | cartservice |
| Node.js | ≥ 20 | currencyservice, paymentservice |
| Python | ≥ 3.11 | emailservice, recommendationservice |
| JDK | ≥ 21 (or use `./gradlew`) | adservice |
| redis-server | any | cart storage |

Install with brew:
```sh
brew install go node python@3.13 openjdk redis
brew install dotnet              # the formula, NOT --cask (cask requires sudo)
```

### Build steps

```sh
# Go services
for svc in frontend productcatalogservice shippingservice checkoutservice; do
  ( cd src/$svc && go build -o /tmp/native/bin/$svc . )
done

# .NET cartservice
( cd src/cartservice/src && dotnet publish -c Release -o /tmp/native/bin/cartservice --self-contained false )

# Java adservice
( cd src/adservice && chmod +x gradlew && ./gradlew installDist )
# binary at: src/adservice/build/install/hipstershop/bin/AdService

# Node services — skip native build scripts (pprof needs Xcode CLT; profiler is disabled anyway)
( cd src/currencyservice && npm install --ignore-scripts )
( cd src/paymentservice  && npm install --ignore-scripts )

# Python services — use venvs
for svc in emailservice recommendationservice; do
  ( cd src/$svc && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt )
done
```

### Run

A launcher script (`run-native.sh up|down`) is in this repo. It starts redis + 10 services with the right env vars on rewired ports and writes PID files to `/tmp/native/run/`.

### Gotchas

- **macOS AirPlay holds ports 5000 and 7000.** Default service ports `5000` (emailservice in compose) and `7000` (currencyservice) collide with macOS Control Center's AirPlay Receiver. The launcher uses `5500` and `7001` instead and re-wires the consumer env vars accordingly.
- **All on one host = port conflicts.** In k8s/compose, multiple services use `PORT=8080` (frontend, recommendationservice, emailservice in different env). On a single host they must be remapped — the launcher uses 8080/8081/5500.
- **cartservice ignores `PORT`** — it's an ASP.NET Core app reading `ASPNETCORE_HTTP_PORTS` (set to `7070` in its Dockerfile). Set that env var, not `PORT`.
- **`pprof` (Node) needs Xcode CLT** to build its native addon. Profiler is disabled at runtime via `DISABLE_PROFILER=1`, so `npm install --ignore-scripts` skips the build harmlessly.
- **`brew install --cask dotnet-sdk` requires sudo** (uses macOS pkg installer). The formula `brew install dotnet` doesn't and gives an equivalent SDK at `/opt/homebrew/opt/dotnet`.
- **Working directory matters.** Frontend reads `templates/` and `static/` relative to CWD; productcatalogservice reads `products.json`. Run each service with CWD set to its `src/<service>/` directory.

### Stop

```sh
./run-native.sh down
```

---

## Decision guide

- **Just want to see it working with the least friction:** Method 1 with prebuilt images (`kubectl apply -f release/kubernetes-manifests.yaml`) — no builds at all.
- **Want to modify code and iterate:** Method 1 with `skaffold dev` (auto-rebuild on file change) — the path the upstream repo is designed for.
- **Don't want k8s in the picture:** Method 2. Light, simple, but you author the compose file.
- **Want bare processes for debugging:** Method 3. Most fragile, most port juggling, but lets you attach a debugger directly.
