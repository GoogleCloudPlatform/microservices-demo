# Live e2e smoke runbook — Online Boutique (microservices-demo)

The `e2e-tester` subagent follows THIS file to prove a change works against the **real, running**
system. It is the contract: prerequisites, entry point, exact steps, expected results,
troubleshooting. Evidence + `summary.md` go to `docs/test/NNN-<slug>/`.

> **Multi-service, Kubernetes-native.** This app has **no local docker-compose** — it runs on a
> Kubernetes cluster via `skaffold`. Until a cluster is up, `work-plan` may declare
> `e2e: n/a — no cluster running` for a unit, and the change is verified by the routed quality gate
> (build/unit tests) plus the task's own acceptance check. Fill a service subsection below once you
> have a cluster and are working on that service.

## Prerequisites (shared bring-up)
- A Kubernetes cluster: local `minikube`/`kind` (`minikube start --cpus=4 --memory 4096`) or a GKE
  cluster. See `docs/development-guide.md`.
- `kubectl`, `skaffold`, and Docker installed and pointed at the cluster.
- Deploy the whole app from the repo root: `skaffold run` (build + deploy) or `skaffold dev`
  (watch + redeploy). Wait for all deployments to become available:
  `kubectl wait --for=condition=available --timeout=600s deployment --all`.
- Reach the storefront: `kubectl port-forward deployment/frontend 8080:8080` then open
  `http://localhost:8080` (or use the `frontend-external` LoadBalancer IP on GKE).
- Use only synthetic / demo data (the app ships a fake product catalog and fake payment). Never
  capture real credentials or PII in evidence.

## Expected verdict
PASS = the documented observable outcomes for the service(s) under test hold. A timeout, a 5xx, an
auth wall, a crashed pod, or fabricated output is a **FAIL** — captured, never a false pass.

## Troubleshooting
- Pod stuck `Pending` → cluster lacks CPU/memory; give minikube more (`--cpus`/`--memory`).
- `ImagePullBackOff` → image not built/pushed; re-run `skaffold run` (or `skaffold dev`).
- `frontend` 500s on load → a downstream gRPC dependency isn't ready; `kubectl get pods` and wait for
  all to be `Running`/`Ready`.

## Services
The dispatch names the service(s) under test; follow that service's subsection only. Fill one
subsection per service the team actually works on (at minimum the routed ones). The two below cover
the primary user-facing flows; add others (cart, shipping, productcatalog, ad) as needed.

### frontend (Go — the storefront UI)
- **Entry point:** `kubectl port-forward deployment/frontend 8080:8080` → `http://localhost:8080`.
- **Steps & expected results:**
  1. Load the home page → product grid renders with items and prices. Capture `01-home.png`.
  2. Open a product, "Add to Cart", go to cart → item shows with quantity. Capture `02-cart.png`.
  3. "Place Order" with the pre-filled demo card → order-confirmation page with a confirmation ID
     and shipping cost. Capture `03-order-confirmed.png`.
  4. Switch currency (e.g. USD → EUR) → prices update. Capture `04-currency.png`.
- **Expected verdict:** PASS = browse → cart → checkout completes and prices/currency render.

### checkoutservice (Go — order orchestration, gRPC)
- **Entry point:** `kubectl port-forward deployment/checkoutservice 5050:5050`; drive via the
  frontend checkout flow above, or a gRPC client (`grpcurl`) against `PlaceOrder`.
- **Steps & expected results:**
  1. Complete a checkout via the frontend (step 3 above) → `checkoutservice` logs show it called
     cart, shipping, payment, and email without error; an order confirmation returns.
  2. Negative: check out with an empty cart → handled gracefully (no 5xx crash).
- **Expected verdict:** PASS = a full order is orchestrated across dependencies and confirmed.

## Evidence & retention
Screenshots are **committed to the repo** as a visual audit trail — kept for the long run. The
discipline is security, not avoidance:
- **Never capture a secret.** Demo/synthetic data only; redact or crop anything sensitive. A secret
  baked into a committed image is permanent in git history.
- **Capture the viewport, not the full page** — enough to prove the step, no more surface to leak.
- **`summary.md` stands alone.** It must read completely without the images.
