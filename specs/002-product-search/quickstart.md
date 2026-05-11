# Quickstart: Product Search by Name

**Feature**: 002-product-search
**Audience**: Engineer implementing or reviewing this feature.

## Prerequisites

- Go 1.22+ installed locally.
- Repo checked out to branch `002-product-search` (created by SpecKit) — see the branch note in `plan.md` regarding eventual merge back to `attendee/cruz-moreno` for CI deployment.
- No new tooling is required.

## Backend: run the catalog service unit tests

The `SearchProducts` RPC is already implemented; this feature **tightens** it.

```bash
cd src/productcatalogservice
go test ./...
```

After tightening (name-only matching, whitespace trim, empty-query short-circuit), the extended `TestSearchProducts` in `product_catalog_test.go` MUST pass with the table below (or its equivalent table-driven form):

| Mock catalogue names | Query | Expected result names |
|---|---|---|
| Alpha One, Delta, Alpha Two, Gamma | `alpha` | Alpha One, Alpha Two |
| (same) | `ALPHA` | Alpha One, Alpha Two |
| (same) | `" alpha "` | Alpha One, Alpha Two |
| (same) | `alp` | Alpha One, Alpha Two |
| (same) | `delta` | Delta |
| (same) | `zzz` | *(empty)* |
| (same) | `""` | *(empty)* |
| Add a product with name `Watch` and description containing `"alpha"` | `alpha` | Alpha One, Alpha Two — but NOT Watch (locks in name-only matching) |

## Frontend: run locally and exercise the search box

```bash
cd src/frontend
# Standard service env wiring (use whatever values are already in use in
# skaffold/dev profiles — no new env vars are introduced by this feature):
export PRODUCT_CATALOG_SERVICE_ADDR=localhost:3550
export CURRENCY_SERVICE_ADDR=localhost:7000
export CART_SERVICE_ADDR=localhost:7070
export RECOMMENDATION_SERVICE_ADDR=localhost:8080
export CHECKOUT_SERVICE_ADDR=localhost:5050
export SHIPPING_SERVICE_ADDR=localhost:50051
export AD_SERVICE_ADDR=localhost:9555
export SHOPPING_ASSISTANT_SERVICE_ADDR=localhost:80
go run .
```

Then in a browser at `http://localhost:8080/`:

1. **Search box visible everywhere.** Confirm the search box is present in the header on `/`, `/product/{id}`, `/cart`, and `/cart/checkout`.
2. **Happy path.** Type `watch` into the search box → submit. URL becomes `/search?q=watch`. Page shows the `Watch` product as a normal product card.
3. **Case-insensitivity.** Repeat with `WATCH` and `Watch`. Same single result.
4. **Substring inside a name.** Type `lass` → submit. Result includes `Sunglasses`.
5. **Whitespace.** Type `  watch  ` (with surrounding spaces) → submit. Same result as plain `watch`.
6. **No results.** Type `laptop` → submit. Page renders the "no results" panel; search box stays visible and is pre-filled with `laptop`.
7. **Empty / whitespace-only.** Submit with the search box empty (or containing only spaces). Confirm the response is `HTTP 302 → /` and the regular catalog view is displayed; no "no results" panel.
8. **Click-through.** From a result card, click the product → land on the existing `/product/{id}` page → add to cart → cart contents update. The detail / cart flow is unchanged.

## End-to-end smoke (optional, if running the full microservices-demo locally via skaffold)

```bash
skaffold dev
# wait for the `frontend-external` route, then open it in a browser
# and walk through steps 1-8 above.
```

No new env vars, no new manifests, no new Helm values are required. If anything in `skaffold`/`helm-chart`/`kubernetes-manifests` would need to change to get this feature running, **stop** — that contradicts the technical constraints in `plan.md`.

## Success signals

- ✅ All extended unit tests in `productcatalogservice` pass (`go test ./...`).
- ✅ Each of the 8 manual steps above behaves as described.
- ✅ `go vet ./...` and `go build ./...` are clean on both services.
- ✅ No diff under `helm-chart/`, `kubernetes-manifests/`, `kustomize/`, `istio-manifests/`, `release/`, `terraform/`, `cloudbuild.yaml`, or `skaffold.yaml`.
- ✅ No new files under `src/` except `src/frontend/templates/search.html` (and possibly one optional `*_test.go` in the frontend).
- ✅ `protos/demo.proto` is byte-for-byte unchanged.

If any of these fail, see `research.md` for the rationale behind the relevant decision before changing direction.
