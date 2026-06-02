# Phase 1 — Data Model: Product Search (thin slice)

**Branch**: `008-product-search` | **Date**: 2026-06-02

This slice introduces **no new entities** and **no schema changes**. The data model is fully described by the existing protobuf types in `protos/demo.proto`. This document records:

1. Which existing entities and fields are used.
2. How they're used (so a future planner / implementer can verify the slice did not silently expand).
3. What the slice deliberately ignores.

---

## Entities

### Product *(existing — `protos/demo.proto:24-44`)*

```protobuf
message Product {
    string id = 1;
    string name = 2;
    string description = 3;
    string picture = 4;
    Money price_usd = 5;
    repeated string categories = 6;
    int32 quantity = 7;
}
```

| Field | Used by this slice? | How |
|---|---|---|
| `id` | Yes | Used in result rendering as the product detail page link target (`/product/{id}`). |
| `name` | **Yes, primary match field** | Case-insensitive substring matched against `query` (TC-002 amended, FR-003, FR-004). |
| `description` | **Yes, secondary match field** | Case-insensitive substring matched against `query` (TC-002 amended). A product matches if EITHER `name` OR `description` contains the query. Per-product de-duplication is implicit (the loop iterates products, not fields). |
| `picture` | Yes (display only) | Rendered as the thumbnail in the result card. Not involved in matching. |
| `price_usd` | Yes (display only) | Rendered as price (after currency conversion) in the result card. Not involved in matching. |
| `categories` | No | Not involved in matching. Spec Out of Scope. |
| `quantity` | No | Not involved in matching. No out-of-stock UI in this slice (Out of Scope). |

**Validation rules**: none introduced. Products are loaded from `products.json` as-is; the slice does no per-field validation.

**State transitions**: none. `Product` is immutable from the perspective of this slice. The catalog is reloaded as a whole (existing behaviour); search has no awareness of mid-flight catalog changes.

### SearchProductsRequest *(existing — `protos/demo.proto:97-99`)*

```protobuf
message SearchProductsRequest {
    string query = 1;
}
```

| Field | Used by this slice? | How |
|---|---|---|
| `query` | Yes | Free-text input. Matched as a case-insensitive substring against `Product.name`. |

**Validation rules**: none enforced at the protobuf or service layer. The frontend trims whitespace and short-circuits empty strings before the call (FR-010). The backend treats any string as valid; semantically, an empty string would match every product, but this is unreachable from the only known caller.

### SearchProductsResponse *(existing — `protos/demo.proto:101-103`)*

```protobuf
message SearchProductsResponse {
    repeated Product results = 1;
}
```

| Field | Used by this slice? | How |
|---|---|---|
| `results` | Yes | A flat list of `Product` references. Order is the natural iteration order from `parseCatalog()` (FR-007). No ranking, no pagination, no result cap (FR-009). |

---

## Storage

`Product` is stored as a JSON object in `src/productcatalogservice/products.json`. Shape sketch (from inspection of the file's structure used by `catalog_loader.go`):

```json
{
  "products": [
    {
      "id": "OLJCESPC7Z",
      "name": "Sunglasses",
      "description": "Add a modern touch...",
      "picture": "/static/img/products/sunglasses.jpg",
      "priceUsd": { "currencyCode": "USD", "units": 19, "nanos": 990000000 },
      "categories": ["accessories"]
    },
    ...
  ]
}
```

The slice **does not modify `products.json`**. It is read-only here (TC-003).

`catalog_loader.go` parses this file at process start. `parseCatalog()` re-parses on demand if `reloadCatalog` is set. This slice changes neither.

---

## In-process state

`productCatalog` struct (`product_catalog.go:28-31`) holds the parsed catalog in memory. The slice does not add fields, indexes, caches, or other state to this struct. **Nothing in this struct is mutated by search.**

No goroutines, no channels, no sync primitives are introduced.

---

## Out of model (explicitly)

To prevent silent scope creep in implementation:

- **No new fields** on `Product` (e.g. `searchable_name`, `name_normalised`, `searchable`).
- **No new tables, no new datastores** (TC-003).
- **No new index structures** in `productCatalog` (e.g. inverted index, trie, map of lowercase-name → product). The match is a linear scan.
- **No new request/response messages.** `SearchProductsRequest` is not extended with `limit`, `offset`, `filters`, `categories`, etc.
- **No new fields on the `Product` template render struct** (`productView` in `handlers.go:148`). Existing fields suffice for result cards.
- **No persistence of search queries.** Queries are not stored anywhere except in existing request logs (which are inherited; no new log fields).

---

## Relationships

There are no relationships between entities introduced by this slice. The existing `Product → Cart`, `Product → Recommendation`, etc. relationships in the wider system are unaffected.
