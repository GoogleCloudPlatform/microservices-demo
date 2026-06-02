# Contract — gRPC `SearchProducts`

**Service**: `hipstershop.ProductCatalogService`
**Method**: `SearchProducts`
**Proto**: `protos/demo.proto` (lines 74, 97–103)
**Status**: existing on the wire; **semantics tightened by this slice** — no proto change.

## Wire shape (unchanged)

```protobuf
service ProductCatalogService {
    ...
    rpc SearchProducts(SearchProductsRequest) returns (SearchProductsResponse) {}
}

message SearchProductsRequest {
    string query = 1;
}

message SearchProductsResponse {
    repeated Product results = 1;
}
```

## Semantic contract (NEW — enforced by this slice)

Given a `SearchProductsRequest{query}` and a catalog `C` of products loaded from `products.json`:

| Aspect | Contract |
|---|---|
| **Match fields** | `Product.name` **OR** `Product.description`. No other field — including `categories`, `id`, `picture`, `quantity` — influences the match. |
| **Match operator** | Case-insensitive substring. A product `p` matches iff `lower(p.name)` contains `lower(query)` as a substring, **OR** `lower(p.description)` contains `lower(query)` as a substring (in Go: `strings.Contains(strings.ToLower(p.Name), strings.ToLower(q)) || strings.Contains(strings.ToLower(p.Description), strings.ToLower(q))`). |
| **De-duplication** | A product appears in `results` at most once, regardless of whether the query matched only its name, only its description, or both. Implicit because the implementation iterates products and decides each product in or out exactly once. |
| **Order** | Results appear in the same order as catalog iteration order (i.e. the order returned by `parseCatalog()`, which is the order of products in `products.json`). No ranking, no scoring, no reordering. |
| **Cap** | No cap. All matching products are returned. |
| **Empty query** | Implementation-defined and unreachable from the canonical caller. The frontend MUST NOT issue `SearchProducts` with an empty or whitespace-only `query`. If called with `query == ""`, the current implementation returns every product (because the empty string is a substring of every name); this is not relied upon and should not be considered part of the contract. |
| **Non-existent match** | Empty `results` slice. Not a gRPC error. |
| **Catalog reload mid-flight** | The contract is evaluated against the catalog snapshot at the time `parseCatalog()` is invoked inside the handler. Mid-flight catalog reloads (controlled by `reloadCatalog`) are not the search feature's concern. |

## Errors

| Condition | Behaviour |
|---|---|
| Successful call (including zero matches) | gRPC OK with `SearchProductsResponse{results: …}`. |
| `products.json` fails to load | The handler returns an empty `results` slice (existing behaviour of `parseCatalog()` on load error). This is technically a contract violation if the caller cannot distinguish empty-catalog-on-disk from load-failure, but it is the existing behaviour of the service and is out of scope to change in this slice. |
| Any other failure | Standard gRPC error mapping inherited from the framework. |

## Out of contract (explicitly)

- The contract does **not** include any of: typo tolerance, fuzzy matching, stemming, lemmatisation, tokenisation, n-grams, learning-to-rank, personalisation, popularity boost, recency boost, category boost.
- The contract does **not** include pagination, sorting, filtering, faceting, or category restriction.
- The contract does **not** include any matching against `categories`, `id`, `picture`, `quantity`, or any other field besides `name` and `description`. (Description IS in contract per the amended TC-002.)

## Test obligations

The implementation in `src/productcatalogservice/product_catalog.go` and its tests in `src/productcatalogservice/product_catalog_test.go` MUST exercise:

1. Exact-name match (Acceptance Scenario 1).
2. Substring match at start, middle, and end of the name (Acceptance Scenario 2).
3. Case-insensitive match — upper-case query, lower-case query, mixed-case query (Acceptance Scenarios 3, 4).
4. Multiple matches in one query (Acceptance Scenario 5).
5. A product whose `description` (but not `name`) contains the query MUST appear in results (Acceptance Scenario 6, amended).
6. A query that matches one product's name and another product's description returns both, each exactly once (Acceptance Scenario 6a).
7. A product whose only matching field is `category` (or any non-name, non-description field) MUST NOT appear (Acceptance Scenario 6b).
8. Zero results returns an empty `results` slice (Acceptance Scenario 7).
9. Result order matches catalog order (FR-007).
10. Special characters (`.`, `*`, parentheses) are treated as literal substring text (Edge Cases).
11. A query longer than any product name OR description returns zero matches (Edge Cases).

See `research.md` R-4 for the canonical test list.
