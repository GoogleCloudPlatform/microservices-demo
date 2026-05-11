# Implementation Plan: Product Search by Name

**Branch**: `002-product-search` | **Date**: 2026-05-11 | **Spec**: [./spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-product-search/spec.md`

## Summary

Add a storefront search box that lets shoppers find products by typing part of a product name. The frontend posts the query to a new `GET /search` route, which calls `ProductCatalogService.SearchProducts(query)` over gRPC and renders the results using the same product-card layout as the home page.

**Key implementation finding from research**: the `SearchProducts` RPC and its messages already exist in [protos/demo.proto](../../protos/demo.proto) and a working (over-permissive) Go implementation already lives in [src/productcatalogservice/product_catalog.go](../../src/productcatalogservice/product_catalog.go). The generated client stubs are already compiled into the frontend's `genproto/` directory. The work is therefore:

1. **Backend** — tighten the existing `SearchProducts` implementation to match the spec exactly (name-only, case-insensitive substring, trimmed; empty query returns empty result set) and extend the existing test to cover the new behaviour.
2. **Frontend** — add an RPC wrapper, a `/search` HTTP handler, a search-results template, and a search box in the shared header. No new services, no new datastore, no new infrastructure config.

## Technical Context

**Language/Version**: Go 1.22+ (matches existing `go.mod` for both `src/frontend` and `src/productcatalogservice`).
**Primary Dependencies**: Existing only — `google.golang.org/grpc`, `github.com/gorilla/mux`, `html/template`, `github.com/sirupsen/logrus`, OpenTelemetry instrumentation. No new modules.
**Storage**: None added. The product catalogue continues to be loaded in-memory by `productcatalogservice` from `productcatalogservice/products.json` via `catalog_loader.go`. Filtering is a linear scan in memory.
**Testing**: `go test ./...` per service. Backend: extend `src/productcatalogservice/product_catalog_test.go` (table-driven unit tests against the `productCatalog` struct, mirroring the existing `TestSearchProducts` pattern). Frontend: smoke-level handler test using `net/http/httptest` if the existing project has a pattern for it; otherwise rely on manual verification per `quickstart.md`.
**Target Platform**: Linux container, same Dockerfiles already in `src/frontend` and `src/productcatalogservice`. Deployed by the existing CI that watches the attendee branch.
**Project Type**: Web service composed of two Go microservices already present in the repo. No new service is introduced.
**Performance Goals**: Search must render end-to-end in < 500 ms on a typical broadband connection at current catalog size (~10 products). With a linear scan and `extraLatency` already capped low, this is comfortably achievable.
**Constraints**:
- MUST NOT add new services.
- MUST NOT add Elasticsearch, Solr, vector DBs, or any new datastore.
- MUST reuse the in-memory catalogue loaded from `productcatalogservice/products.json`; filtering is in-memory.
- MUST stay in Go for both services and reuse the existing protobuf/gRPC patterns.
- MUST NOT add Helm charts, Kubernetes manifests, environment variables, or pipeline changes.
- MUST stay on the current feature branch; build pipeline is untouched.
**Scale/Scope**: Current catalog ~10 products. Worst-case linear scan over ~10 strings per request is trivial. No pagination, ranking, or relevance scoring in scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The repository's `.specify/memory/constitution.md` is still the unfilled template — no project-specific principles have been ratified. There are therefore **no concrete constitutional gates to enforce**. The plan instead defers to prudent defaults that match the spirit of common SpecKit constitutions:

| Default principle (no explicit constitution) | Status | Notes |
|---|---|---|
| Simplicity / YAGNI | ✅ PASS | Linear scan, no new dependencies, no new services, no new infra. |
| Reuse-first | ✅ PASS | Reuses existing RPC (already in proto + already implemented), existing template/handler/RPC patterns, existing in-memory loader. |
| Test-first / parity | ✅ PASS | Backend tests already cover `SearchProducts`; will be extended for name-only, case, whitespace, empty, no-match cases. |
| No new infra / no new env vars | ✅ PASS | No Helm/manifest/env changes. |
| Inter-service contract stability | ✅ PASS | Proto contract is unchanged — both messages already exist in `demo.proto`. Generated code already in place. |

**Constitution gate result**: PASS. Re-check after Phase 1 design — also PASS (no design choices add new dependencies, services, or surface area beyond what the existing proto already declares).

## Project Structure

### Documentation (this feature)

```text
specs/002-product-search/
├── plan.md                       # This file
├── research.md                   # Phase 0 output
├── data-model.md                 # Phase 1 output
├── quickstart.md                 # Phase 1 output
├── contracts/
│   ├── search-products.proto.md  # gRPC contract excerpt + semantics
│   └── http-search.md            # Frontend HTTP route contract
├── checklists/
│   └── requirements.md           # From /speckit-specify (all items pass)
└── tasks.md                      # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
protos/
└── demo.proto                    # UNCHANGED — SearchProducts + messages already present

src/productcatalogservice/        # Go service — MODIFY
├── product_catalog.go            # MODIFY: tighten SearchProducts to name-only,
│                                 #         trim whitespace, return empty results
│                                 #         for empty/whitespace queries
├── product_catalog_test.go       # MODIFY: extend TestSearchProducts; add cases
│                                 #         for case-insensitive match, substring
│                                 #         match inside a name, whitespace-trim,
│                                 #         empty query, name-only (must NOT
│                                 #         match on description), no-match query
├── catalog_loader.go             # UNCHANGED — existing in-memory loader is the source
├── genproto/                     # UNCHANGED — already has SearchProducts stubs
└── products.json                 # UNCHANGED — source data

src/frontend/                     # Go service — MODIFY
├── main.go                       # MODIFY: register r.HandleFunc(baseUrl+"/search",
│                                 #         svc.searchHandler).Methods(GET)
├── rpc.go                        # MODIFY: add searchProducts(ctx, query) wrapper
│                                 #         mirroring getProducts / getProduct
├── handlers.go                   # MODIFY: add searchHandler — read q from query
│                                 #         string, trim, empty -> redirect to "/",
│                                 #         call searchProducts, render search.html
├── templates/
│   ├── header.html               # MODIFY: add <form action="/search" method="GET">
│   │                             #         with <input name="q"> inside the existing
│   │                             #         sub-navbar; reachable from every page
│   └── search.html               # NEW: results page; reuses product-card markup
│                                 #         from home.html via a shared template
│                                 #         (or inline duplication for simplicity);
│                                 #         renders "no results" panel when the
│                                 #         results slice is empty
└── genproto/                     # UNCHANGED — already has SearchProducts stubs
```

**Structure Decision**: Two-service Go monorepo — exactly the structure already on disk. No new top-level directories. All edits land under `src/frontend/` and `src/productcatalogservice/`.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified.

No constitution violations to justify — table intentionally empty.

## Branch / CI note (informational, not a constitution violation)

The mandatory `before_specify` git hook switched the working branch from `attendee/cruz-moreno` to `002-product-search`. The CI deploys whatever lands on `attendee/cruz-moreno`. To exercise the feature on the deployed environment, the implementation work either needs to be merged back into `attendee/cruz-moreno`, or the implementation can be cherry-picked / replayed on that branch after the spec artifacts are reviewed. This plan does NOT modify CI; it only flags the branch geometry so `/speckit-tasks` and `/speckit-implement` consumers can plan the merge step.
