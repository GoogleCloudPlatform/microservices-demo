# Design Doc: Product Category Filtering
**Status:** Draft  **Author:** Engineering Team  **Date:** 2026-05-26

## Background

Online Boutique's product catalog is served by `productcatalogservice`, a Go microservice that loads a static JSON file (`products.json`) at startup. It exposes two relevant RPCs: `ListProducts` (returns all products) and `SearchProducts` (substring match on name and description). Neither supports filtering by category.

The current `SearchProductsRequest` proto has a single field:

```protobuf
message SearchProductsRequest {
  string query = 1;
}
```

Products in the catalog each carry a `categories` field (a list of strings), but this field is only used for display — it is never used as a filter criterion. The full category taxonomy is a closed set of 9 values (`accessories`, `clothing`, `tops`, `footwear`, `hair`, `beauty`, `decor`, `home`, `kitchen`) defined by the contents of `products.json`.

This design adds a `categories` filter to `SearchProductsRequest` and plumbs it from the frontend UI through to the catalog service.

## Current State

### Who calls ProductCatalogService today

Three services call `ProductCatalogService`:

1. **`frontend`** — calls `ListProducts` to render the home page product grid, and calls `SearchProducts` to render search results. Also calls `GetProduct` for individual product detail pages.
2. **`checkoutservice`** — calls `GetProduct` per line item during `PlaceOrder` to retrieve current price for each product in the cart. Does NOT call `ListProducts` or `SearchProducts`.
3. **`recommendationservice`** — calls `ListProducts` to get the full product list, then randomly selects from it to build a recommendation set. Does NOT call `SearchProducts`.

Only `frontend` calls `SearchProducts`. The category filter change is therefore primarily a `frontend` + `productcatalogservice` concern, but the proto change to `SearchProductsRequest` touches a shared interface and requires care.

### Products.json structure (relevant excerpt)

Each product entry has a `categories` array, e.g.:
```json
{
  "id": "OLJCESPC7Z",
  "name": "Vintage Record Player",
  "categories": ["music", "electronics"]
}
```

(The exact categories vary; the closed set of valid values is enforced by convention, not schema validation.)

## Proposed Solution

### 1. Proto change: SearchProductsRequest

Add an optional `repeated string categories` field at field number 2:

```protobuf
message SearchProductsRequest {
  string          query      = 1;
  repeated string categories = 2;  // NEW: if empty, no category filter is applied
}
```

Field 2 is unset (empty repeated field) by default in proto3. Existing callers that send only `query` will receive the current behavior with no change. A caller can now send:
- Only `query` — text search, no category filter (existing behavior)
- Only `categories` — category-only filter, no text matching
- Both `query` and `categories` — text search within the specified categories

The `SearchProductsResponse` proto is unchanged.

### 2. ProductCatalogService changes

In the `SearchProducts` handler, after the existing substring match loop, apply a category filter if `categories` is non-empty:

```
for each product in catalog:
  if query is non-empty and product does not contain query substring → skip
  if categories is non-empty and product.categories ∩ request.categories is empty → skip
  include product in results
```

The filter is an OR across the requested categories (include if the product belongs to any of the listed categories).

No change to `ListProducts` or `GetProduct`. No database involved — the catalog is still in-memory from the JSON file loaded at startup. No restart or catalog rebuild is needed for this code change alone; however, adding a new category to the UI requires a products.json change and container rebuild.

There is no new proto service or new service deployment. `productcatalogservice` is updated in-place.

### 3. Frontend changes

**Home page (`/`):**
- Call `ProductCatalogService.ListProducts` to get the full product list (current behavior).
- Extract the unique set of categories from the returned products to build the filter chip list dynamically. This ensures the displayed categories always reflect what is actually in the catalog.
- When the user selects one or more category chips, re-fetch using `SearchProducts` with the selected categories (and empty `query`), or with both `query` and `categories` if a search term is also present.
- Render category chips above the product grid. Active filters are visually distinct. A "Clear" control removes all filters.

**Search results page:**
- The existing text search already calls `SearchProducts` with `query`. Extend this to also include selected `categories` from the filter UI.
- Category chips are added above search results using the same component as the home page.

**URL state:**
- Active categories are written to query params: `?category=clothing&category=tops`.
- On page load, parse query params and pre-select matching chips. This makes filtered views bookmarkable and shareable, and supports browser back/forward navigation correctly.

**No changes to:**
- The cart or checkout flow.
- Any gRPC calls outside of `SearchProducts` and `ListProducts`.
- The product detail page.

### 4. No changes to recommendationservice or checkoutservice

`recommendationservice` calls `ListProducts`, which is unchanged. `checkoutservice` calls only `GetProduct`, which is unchanged. Neither service needs to be touched.

## Affected Services

| Service | Change |
|---|---|
| `productcatalogservice` | Updated `SearchProducts` handler to apply category filter; no proto file ownership change |
| `frontend` | Category filter UI on home page and search results; updated `SearchProducts` calls to pass `categories`; URL param handling |
| `recommendationservice` | No changes; uses `ListProducts` only |
| `checkoutservice` | No changes; uses `GetProduct` only |
| `cartservice` | No changes |
| `paymentservice` | No changes |
| `shippingservice` | No changes |
| `emailservice` | No changes |
| `currencyservice` | No changes |
| `adservice` | No changes |

## API / Proto Changes

**`demo.proto` — SearchProductsRequest:**

```protobuf
// Before
message SearchProductsRequest {
  string query = 1;
}

// After
message SearchProductsRequest {
  string          query      = 1;
  repeated string categories = 2;
}
```

All other messages and services in `demo.proto` are unchanged. The change is backward compatible: proto3 treats a missing repeated field as an empty list, which maps to "no filter" in the updated handler.

**Generated code:** Go stubs for `productcatalogservice` and `frontend` must be regenerated from the updated proto. The generated Go struct gains a `Categories []string` field. Existing code that constructs `SearchProductsRequest{Query: q}` will compile without modification.

## Deployment Plan

1. Update `demo.proto` — add `categories` field 2 to `SearchProductsRequest`.
2. Regenerate proto stubs for Go (frontend, productcatalogservice).
3. Update `productcatalogservice` search handler to apply category filter.
4. Update `frontend` with category filter UI and updated RPC call.
5. Deploy `productcatalogservice` first, then `frontend`. Because the new field is optional and backward compatible, both old and new versions can run simultaneously during a rolling update without errors.
6. Validate on staging: test category-only filter, text-only search (existing), combined filter, and zero-result state.

Rollback: revert `frontend` to previous binary (hides UI); `productcatalogservice` can remain at the new version since callers that omit `categories` are unaffected.

## Risks & Open Questions

**Category data lives in products.json, not a database.** The closed category set is enforced by convention only. If a product is added to the JSON file with a typo in its category (e.g., `"clothng"`), that typo will appear as a category chip in the UI. A validation step in the catalog load path (fail fast on startup if an unrecognized category value is found) would prevent silent data issues but would also require updating that validation whenever the taxonomy expands.

**Static catalog means no runtime category management.** Adding a new category requires editing `products.json` and rebuilding and redeploying `productcatalogservice`. This is a deliberate constraint of the current architecture, not a bug, but product managers should be aware that "can we add a new category?" is not a configuration change.

**Recommendationservice receives unfiltered results.** `recommendationservice` calls `ListProducts` and does not apply any category filter. Recommendations remain random across the full catalog regardless of what category the user is currently browsing. This is a known UX limitation and is out of scope.

**Proto stub regeneration must be coordinated.** If a developer manually constructs a `SearchProductsRequest` proto binary (e.g., in a test harness or integration test), the binary encoding of field 2 must not conflict. Because field 2 is a new field, existing serialized `SearchProductsRequest` binaries on the wire are unaffected — proto3 unknown fields are ignored by older receivers. However, any service that reads `SearchProductsRequest` from a persistent store or queue (there are none currently) would need to be audited.

**Performance:** `productcatalogservice` holds all 9 products in memory. The category filter is an in-memory loop. There is no performance concern at current catalog scale.
