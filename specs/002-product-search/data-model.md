# Phase 1 Data Model: Product Search by Name

**Feature**: 002-product-search
**Date**: 2026-05-11

The feature introduces **no new persisted entities**. It defines two transient (in-request) values and reuses one existing entity.

## Entities

### Product *(existing — unchanged)*

The canonical `Product` message defined in [protos/demo.proto](../../protos/demo.proto):

| Field | Type | Notes |
|---|---|---|
| `id` | `string` | Used by frontend to build `/product/{id}` links from results. |
| `name` | `string` | **Only field consulted during matching.** |
| `description` | `string` | Returned but never matched against. |
| `picture` | `string` | Returned, rendered on result cards. |
| `price_usd` | `Money` | Returned, rendered on result cards. |
| `categories` | `repeated string` | Returned, not used by search. |

No fields are added, removed, or repurposed.

### SearchQuery *(transient)*

A request-scoped value owned by the frontend handler.

| Field | Type | Validation / Normalisation |
|---|---|---|
| `raw` | `string` | The URL query parameter `q` as supplied by the browser. |
| `normalised` | `string` | `strings.TrimSpace(raw)`. If empty, the handler short-circuits with a 302 to `/`. |

`normalised` is what is sent in `SearchProductsRequest.query`.

State transitions:

```text
raw  ──TrimSpace──▶  normalised
                      │
                      ├─ empty ──▶ HTTP 302 redirect to "/"
                      └─ non-empty ──▶ SearchProducts(query=normalised)
```

### SearchResult *(transient)*

Owned by `productcatalogservice` for the duration of the RPC and by the frontend handler for the duration of the HTTP response.

| Field | Type | Notes |
|---|---|---|
| `query` | `string` | Echoes `SearchProductsRequest.query` so the UI can pre-fill the search box and the "no results" message. |
| `results` | `repeated Product` | Subset of the in-memory catalogue whose `name` (lower-cased) contains the lower-cased `query` as a substring. Order preserves the order returned by `parseCatalog()`. |

Validation / invariants:

- `len(results) == 0` is a valid state and triggers the "no results" panel.
- `results` is never `nil` from the wire perspective (proto generates a non-nil but possibly empty slice).
- Result set is read-only — the search operation does not mutate the catalog, the cart, or any other system state (FR-011).

## Relationships

```text
SearchQuery (frontend handler)
   │  q (trimmed)
   ▼
SearchProductsRequest  ── gRPC ──▶  productcatalogservice.SearchProducts
                                         │
                                         │ linear scan over parseCatalog()
                                         │ matches name substring (case-insensitive)
                                         ▼
                                  SearchProductsResponse{ results: []Product }
   ▲
   │ template binding
   │
SearchResult (frontend handler) ──▶ templates/search.html
```

## Out-of-scope (explicit)

- Persistence: nothing is stored. No DB rows, no cache entries, no search index.
- Telemetry entities: existing logs/traces are sufficient; no new metrics or counters added by this feature.
- Per-user state: search is anonymous and stateless beyond the session cookie that already exists for the storefront.
