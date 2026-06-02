# Implementation Plan: Product Search (thin slice)

**Branch**: `008-product-search` | **Date**: 2026-06-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-product-search/spec.md`

## Summary

A shopper-facing product search. A search input lives in the storefront header (visible on every page). When the shopper submits a non-empty query, the frontend issues a gRPC call to `SearchProducts(query)` on `productcatalogservice`; the service returns products whose **`name` OR `description`** field contains the query as a **case-insensitive substring**. Results render on `/search?q=…`. Empty queries are short-circuited at the frontend with a helper message — no backend call.

**Critical reality check (post-amendment)**: roughly 95% of the slice is **already implemented on this branch** (`008-product-search`, branched from `attendee/matthew-buckland`). Proto, gRPC method, handler, `/search` route, header search form, results template — and the name-OR-description match logic — all exist. The spec has been amended to keep the description-match arm (the workshop's prior "restore description match" commit aligns with the intended spec). The plan therefore reduces to **two non-code-changing items** plus a small UI polish and test coverage.

## Pre-implementation reality vs. spec (READ FIRST)

| Spec element | What exists today on this branch | Delta to satisfy spec |
|---|---|---|
| TC-001: `SearchProducts(query)` RPC on `productcatalogservice` | **Present.** Defined in `protos/demo.proto` line 74; `SearchProductsRequest{query}` / `SearchProductsResponse{repeated Product results}` already generated into both services' `genproto/`. | **No change.** TC-001 reads "new" but the method already exists with the right shape. Re-frame TC-001 as "**use** the existing method." |
| TC-002: case-insensitive substring on `name` OR `description` | **Match.** `product_catalog.go:60-72` matches on `name` OR `description` via `strings.ToLower` substring. The recent commit `736cf79b` *restored* the description arm after a seed bug removed it. The amended spec endorses this. | **No change.** TC-002 is satisfied by the existing implementation as-is. |
| TC-003: in-memory filtering over `products.json` | **Present.** `parseCatalog()` loads `products.json` via `catalog_loader.go`; `SearchProducts` iterates it in process. | **No change.** |
| TC-004: Go + existing protobuf/gRPC patterns | **Present.** Both services are Go; both consume the same generated stubs. | **No change.** |
| TC-005..TC-007: no new services / infra / pipeline | n/a (no edits planned to those) | **No change.** |
| TC-008: deploys via merge to `attendee/matthew-buckland` | Branch is set up correctly. | **Merge at the end** of `/speckit-implement`. |
| FR-001: search input in global header on every page | **Present.** `templates/header.html:67-72` defines a `<form action="/search">` inside the shared header included by every other template. | **No change.** |
| FR-002: accepts ≥1 char free text | **Present.** `<input type="text" name="q">`, no minlength enforcement. | **No change.** |
| FR-003 / FR-004: name-or-description matching | **Match** (see TC-002 above). | **No change.** |
| FR-005: result shows name + link to detail page | **Present.** `templates/search.html:37-48` shows name, price, image, link to `/product/{id}`. (Image and price are extras over the spec minimum; spec is met.) | **No change.** |
| FR-006: empty-state message when zero matches | **Partial.** `templates/search.html:30` shows "0 products found" but no explicit "no products were found" prose or guidance. | **Minor template change.** Add an explicit empty-state block. |
| FR-007: natural order from catalog service | **Present.** Backend returns results in catalog iteration order; frontend does not reorder. | **No change.** |
| FR-008: storefront still loads if catalog service is down | **Partial.** `searchHandler` calls `renderHTTPError` on RPC failure, returning HTTP 500 to the shopper. The storefront itself (non-search pages) is unaffected by `productcatalogservice` outages only inasmuch as those pages don't call it at request time — many do, so this resilience is a property of the wider Online Boutique design, not the search feature alone. | **Document, don't change.** Add a research note that catalog-down resilience is inherited from existing storefront behaviour; we are not introducing a new failure mode. Optionally improve `searchHandler` to render a soft inline error instead of HTTP 500 — flagged as an optional improvement, not blocking. |
| FR-009: no result cap | Backend returns all matches; frontend renders all. | **No change.** |
| FR-010: empty query → helper message, no backend call | **Present.** `handlers.go:124,134` trims whitespace and only calls `searchProducts` when `query != ""`. `search.html:31-34` shows "Enter a term in the search bar above..." when `query` is empty. | **No change.** (Verbiage differs slightly from "Type a product name to search" — close enough; not worth editing.) |
| SC-001..SC-005 | Verifiable in test / staging. | **Add tests** (see Phase 1). |
| SC-006, SC-007 | Measured post-launch from logs. | **Out of slice.** |

**Summary of code changes required (after spec amendment):**

1. ~~`src/productcatalogservice/product_catalog.go`~~ — **No change.** Existing name-OR-description logic matches the amended spec.
2. `src/productcatalogservice/product_catalog_test.go` — add tests covering case-insensitivity, substring positions on both name and description, multiple matches, description-only-DOES-match (regression guard for the workshop's seed bug), category-only-must-not-match, and empty/whitespace handling.
3. `src/frontend/templates/search.html` — add explicit empty-state block when `query` is non-empty but `products` is empty.
4. *(Optional, not blocking)* `src/frontend/handlers.go` — soften the catalog-service-down error path from HTTP 500 to an inline error.

**Net: zero changes to the Go backend code, one template edit, one test-file extension.** No new files. No proto changes. No infra changes.

## Technical Context

**Language/Version**: Go. `productcatalogservice` and `frontend` are both Go services with their own `go.mod`. No version bump required for this slice.

**Primary Dependencies**: existing only — `google.golang.org/grpc`, `github.com/golang/protobuf`, `github.com/sirupsen/logrus`. No new dependencies introduced.

**Storage**: in-memory load of `src/productcatalogservice/products.json` via `catalog_loader.go` (called by `parseCatalog`). File-backed JSON, parsed at startup, optionally reloaded when `reloadCatalog` is set. No database, no external index.

**Testing**: `go test ./...` in each service's module. The existing test file `product_catalog_test.go` already covers `SearchProducts` for a single positive case ("alpha" → 2 matches); we extend it with table-driven tests for the full FR/SC matrix. No new test framework. Frontend handler tests are optional and not blocking.

**Target Platform**: existing Kubernetes deployment via the existing CI pipeline. Linux containers built by the existing Dockerfiles. TC-005..TC-007 explicitly forbid changing any of this.

**Project Type**: polyglot microservices repository; this slice modifies two existing Go services. No new service.

**Performance Goals**: SC-003 — results (or empty state) on screen ≤ 2s at p95. With ~10 products in `products.json` and an in-memory `strings.Contains` loop, the backend scan is microseconds; the wall-clock budget is dominated by template render + network. Trivially achievable.

**Constraints**: TC-001..TC-008 (hard, non-negotiable). The 15 explicit Out of Scope items in the spec apply.

**Scale/Scope**: ~10 products today. Spec defers scale concerns. No multi-locale.

## Constitution Check

`.specify/memory/constitution.md` is the **unfilled template** — no project principles or governance gates have been ratified. **All constitution gates pass vacuously.**

Recommend running `/speckit-constitution` separately at some point to populate this file. Not required for this slice to proceed.

Re-evaluation after Phase 1 design (below): unchanged — vacuous pass.

## Project Structure

### Documentation (this feature)

```text
specs/008-product-search/
├── plan.md                       # This file (/speckit-plan output)
├── spec.md                       # Feature specification
├── research.md                   # Phase 0 output
├── data-model.md                 # Phase 1 output
├── quickstart.md                 # Phase 1 output
├── contracts/                    # Phase 1 output
│   ├── search-products.grpc.md   # gRPC contract (existing proto)
│   └── frontend-search.http.md   # HTTP contract (existing route)
├── checklists/
│   └── requirements.md           # Spec quality checklist
└── tasks.md                      # Phase 2 — produced by /speckit-tasks (not this command)
```

### Source code (real paths in this repo)

```text
src/productcatalogservice/
├── product_catalog.go            # NO CHANGE — existing name-OR-description logic matches amended spec
├── product_catalog_test.go       # MODIFY — extend tests for FR/SC coverage
├── products.json                 # READ-ONLY (TC-003)
├── server.go                     # NO CHANGE
├── catalog_loader.go             # NO CHANGE
└── genproto/                     # NO CHANGE (already includes SearchProducts*)

src/frontend/
├── handlers.go                   # READ-ONLY (optional soft-error tweak in resilience improvement)
├── rpc.go                        # NO CHANGE (searchProducts wrapper exists)
├── templates/header.html         # NO CHANGE (form already present, header included by all pages)
├── templates/search.html         # MODIFY — add explicit empty-state block
└── genproto/                     # NO CHANGE

protos/demo.proto                 # NO CHANGE (SearchProducts already defined line 74)
```

**Structure decision**: this slice is a minimal, surgical modification to one existing Go service template + a test extension. **No new packages, no new files, no new modules, no Go behavioural changes.** The footprint is one template addition and a test-file extension.

## Phase 0 — research

See [research.md](./research.md). All `[NEEDS CLARIFICATION]` markers in the spec are already resolved; Phase 0 covers:

- The spec ↔ code conflict and its resolution.
- Locking down the case-folding semantics (ASCII-only vs Unicode).
- Empty / whitespace handling — where to enforce.
- Test strategy: table-driven, what to cover, what to deliberately *not* test (per Out of Scope).
- Resilience: how the existing storefront behaves when `productcatalogservice` is unreachable, and whether this slice needs to improve that.

## Phase 1 — design & contracts

See [data-model.md](./data-model.md), [contracts/](./contracts/), and [quickstart.md](./quickstart.md).

### Entities

- **Product** — existing protobuf message. No schema change. Search uses the `name` field only.
- **SearchProductsRequest{query: string}** — existing protobuf. No change.
- **SearchProductsResponse{repeated Product results}** — existing protobuf. No change.

### Contracts

- **gRPC** (`contracts/search-products.grpc.md`): formalises the *semantics* the spec attaches to the existing `SearchProducts` method. The wire shape doesn't change; the documented behaviour tightens.
- **HTTP** (`contracts/frontend-search.http.md`): formalises the contract of `GET /search?q=…` exposed by `frontend`.

### Agent context

`CLAUDE.md` is updated to point at this plan within the SpecKit section.

## Complexity Tracking

No constitution violations exist (constitution is empty). Nothing to justify.

If a constitution is added later that forbids e.g. "modifying generated stubs without a contract test," this slice already complies — no generated stubs are touched.

## Open follow-ups (not blocking implementation)

These are intentionally left for separate work; flagged so the user knows they were considered and excluded:

1. ~~**Workshop-narrative tension.**~~ **Resolved 2026-06-02**: user chose to preserve description matching. Spec amended (TC-002, FR-003, FR-004, Acceptance Scenarios 6/6a/6b, SC-001, SC-002, Out of Scope). The existing code already satisfies the amended TC-002, so no Go behavioural change is required.
2. **Catalog-service-down soft error** (FR-008) — currently returns HTTP 500. Could degrade more gracefully to an inline error on the search page. Out of slice unless the user wants it.
3. **Unicode case folding** (Edge Cases, spec) — `strings.ToLower` in Go does Unicode case folding for BMP characters, which is fine for the demo catalog. A full ICU-level implementation is out of slice.
