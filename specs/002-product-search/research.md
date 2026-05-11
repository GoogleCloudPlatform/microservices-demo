# Phase 0 Research: Product Search by Name

**Feature**: 002-product-search
**Date**: 2026-05-11

## R-1 — Does `SearchProducts` already exist?

- **Decision**: Reuse the existing `SearchProducts` RPC defined in [protos/demo.proto](../../protos/demo.proto) (lines 74, 97–103). Do **not** introduce a new RPC.
- **Rationale**: The contract `SearchProducts(SearchProductsRequest{query}) → SearchProductsResponse{results: repeated Product}` is already declared in the shared proto and the generated client/server code is already compiled into both `src/productcatalogservice/genproto` and `src/frontend/genproto` (grep confirms ~40 occurrences across the two `.pb.go` files in the frontend alone). Re-declaring it would churn generated code, fight CI, and risk wire-incompatibility with other clients.
- **Alternatives considered**:
  - *Add a new RPC `SearchProductsByName`* — rejected: extra surface area, doesn't satisfy the "reuse existing protobuf/gRPC patterns" constraint, and the existing RPC already takes a `query` string.
  - *Search client-side in the frontend* — rejected: the frontend would need to `ListProducts` on every query, which is wasteful and bleeds business logic into the UI layer.

## R-2 — Where does the catalog live, and how should we filter?

- **Decision**: Filter in-process in `productcatalogservice` using a linear scan over the slice returned by `parseCatalog()`, doing a `strings.Contains(strings.ToLower(name), strings.ToLower(query))` after trimming the query with `strings.TrimSpace`.
- **Rationale**: The catalogue is loaded from `products.json` into memory at startup (see `catalog_loader.go` and `productCatalog.parseCatalog` in [product_catalog.go](../../src/productcatalogservice/product_catalog.go)). With ~10 products today, linear scan is O(n) on tens of strings — orders of magnitude under the 500 ms render budget. No index, cache, or external store is justified.
- **Alternatives considered**:
  - *Lower-case the catalog once at load time and reuse* — rejected for now: micro-optimisation; would add a parallel slice that has to be kept in sync with the existing `parseCatalog()`/`reloadCatalog` flow. Revisit only if the catalog grows by 2+ orders of magnitude.
  - *Regex matching* — rejected: exposes regex injection / DOS surface to user input; substring is simpler and meets the spec.
  - *Bring in Elasticsearch / Solr / a vector DB* — explicitly forbidden by the technical constraints and overkill for this dataset.

## R-3 — Should matching include the description as the current code does?

- **Decision**: Match **on `name` only**. Tighten the existing implementation by removing the `strings.Contains(strings.ToLower(product.Description), …)` clause.
- **Rationale**: Spec FR-002 and FR-004 are explicit: matching considers the name field only. The current implementation in [product_catalog.go:60-72](../../src/productcatalogservice/product_catalog.go) also OR-matches description, which would over-return (e.g. `"watch"` would match products whose description mentions watching TV). Bringing the implementation into line with the spec is a one-line change.
- **Alternatives considered**:
  - *Leave name+description match in place* — rejected: violates FR-002/FR-004 and creates surprising matches.
  - *Match name AND description* — rejected: too restrictive, would return zero results for legitimate queries.
  - *Add a feature flag for name-vs-name+description* — rejected: violates the no-new-env-vars constraint, and YAGNI.

## R-4 — How does the frontend currently call the catalog?

- **Decision**: Add `searchProducts(ctx, query)` to `src/frontend/rpc.go`, modelled after the existing `getProducts` and `getProduct` helpers there.
- **Rationale**: The frontend already opens a single gRPC connection to `productcatalogservice` and creates a typed client per call (`pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn)`); see lines 45–55 of `rpc.go`. Adding a third helper mirrors the existing pattern exactly. Re-uses the existing connection, tracing, and propagation set up in `main.go`.
- **Alternatives considered**:
  - *Inline the gRPC call inside the HTTP handler* — rejected: breaks the project's house style (every catalog call goes through `rpc.go`).

## R-5 — How is the storefront UI rendered, and where should the search box live?

- **Decision**: Add a `<form action="{{ $.baseUrl }}/search" method="GET">` block with a single `<input name="q">` inside the existing `sub-navbar` in [src/frontend/templates/header.html](../../src/frontend/templates/header.html). Add a new template `src/frontend/templates/search.html` for the results page. Reuse the same product-card markup the home page uses (either via a shared sub-template or pragmatic duplication if no sub-template extraction is already in use).
- **Rationale**: `header.html` is included on every page (it's the `{{ define "header" }}` block consumed by all top-level templates), so a search box there satisfies FR-009 ("reachable from every storefront page") with zero per-page edits. `GET /search?q=…` keeps the operation read-only, idempotent, bookmarkable, and consistent with the rest of the frontend's GET-vs-POST split.
- **Alternatives considered**:
  - *Search box only on the home page* — rejected: violates FR-009.
  - *POST `/search`* — rejected: search is read-only; GET preserves back/forward, sharability, and matches the pattern used by `/product/{id}` and `/cart`.
  - *Client-side JS-only search-as-you-type* — out of scope for this version; would also require a separate JSON endpoint. Server-rendered submit is enough for v1 and matches the rest of the storefront.

## R-6 — How should we handle empty / whitespace-only queries?

- **Decision**: In the frontend handler, trim `q`. If empty, **HTTP 302 redirect to `/`** rather than render a "no results" page. Send the trimmed query (if non-empty) to `SearchProducts`.
- **Rationale**: FR-006 says empty/whitespace queries must not show a "no results" state and should return the shopper to the regular catalog view. Redirecting to `/` is the cleanest implementation, preserves URL hygiene (no `?q=` lingering), and matches existing patterns where the catalog is the default landing.
- **Alternatives considered**:
  - *Render the home template directly from the handler* — rejected: duplicates rendering logic; a redirect is one line.
  - *Render a friendly "type something to search" panel* — rejected: spec calls for idle state = regular catalog view.

## R-7 — Testing strategy

- **Decision**:
  - **Backend**: extend `TestSearchProducts` in `product_catalog_test.go` with table-driven cases for: exact match, mixed-case match, substring inside name (e.g. `"alp"` → 2 products), leading/trailing whitespace, empty query (expect 0 results), no-match query (expect 0 results), description-only term (must now return 0 results to lock in name-only matching).
  - **Frontend**: smoke-test the handler with `net/http/httptest` only if the repo's existing convention supports it (currently no `*_test.go` files exist under `src/frontend/` — so a single new test there is optional; manual verification per `quickstart.md` is the fallback for v1).
- **Rationale**: Mirrors the existing `product_catalog_test.go` pattern (table-style `TestMain` with `mockProductCatalog`). Pragmatic given the frontend has no existing handler-test scaffolding.
- **Alternatives considered**:
  - *End-to-end browser test* — out of scope; would require a Cypress/Playwright addition the repo doesn't have.
  - *Skip backend tests* — rejected: `TestSearchProducts` already exists and would silently keep passing against the wrong semantics if we don't tighten it.

## Resolved NEEDS CLARIFICATION

None — the spec carried zero `[NEEDS CLARIFICATION]` markers into planning.
