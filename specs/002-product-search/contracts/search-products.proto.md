# Contract: `ProductCatalogService.SearchProducts` (gRPC)

**Status**: Pre-existing in [`protos/demo.proto`](../../../protos/demo.proto). This document records the semantics the implementation MUST honour for this feature; the wire schema is unchanged.

## Wire schema (excerpt, unchanged)

```proto
service ProductCatalogService {
  // ...
  rpc SearchProducts(SearchProductsRequest) returns (SearchProductsResponse) {}
}

message SearchProductsRequest {
  string query = 1;
}

message SearchProductsResponse {
  repeated Product results = 1;
}
```

`Product` is the existing message in the same file; no fields are added or changed.

## Semantics (this feature)

| Aspect | Behaviour |
|---|---|
| Matching field | **`Product.name` only.** Description, categories, and ID are NOT matched. |
| Match style | Case-insensitive substring (`strings.Contains(strings.ToLower(name), strings.ToLower(query))`). |
| Whitespace | Caller is expected to send a trimmed query. The server tolerates leading/trailing whitespace by trimming defensively (`strings.TrimSpace(query)`). |
| Empty query | Returns `SearchProductsResponse{results: []}`. The server does NOT return `ListProducts`-equivalent data and does NOT error. |
| No matches | Returns `SearchProductsResponse{results: []}` with `OK` status. |
| Result order | Preserves the existing catalog order returned by `parseCatalog()`. No ranking, scoring, or randomisation. |
| Side effects | None. The RPC is read-only. |
| Errors | Standard gRPC errors only (e.g. unavailable, deadline exceeded). No new error codes introduced. |
| Latency budget | Inherits the existing `extraLatency` simulation already in `productcatalogservice`. Real work is O(N) over the in-memory catalog, ≪ 1 ms at current size. |

## Behaviour matrix (test oracle)

Using the mock catalogue already set up in `product_catalog_test.go`:

| Products (name) | Query | Expected `results` (names) |
|---|---|---|
| `Product Alpha One`, `Product Delta`, `Product Alpha Two`, `Product Gamma` | `"alpha"` | `[Product Alpha One, Product Alpha Two]` |
| (same) | `"ALPHA"` | `[Product Alpha One, Product Alpha Two]` |
| (same) | `" alpha "` | `[Product Alpha One, Product Alpha Two]` *(server trims)* |
| (same) | `"alp"` | `[Product Alpha One, Product Alpha Two]` *(substring match)* |
| (same) | `"delta"` | `[Product Delta]` |
| (same) | `"zzz"` | `[]` |
| (same) | `""` | `[]` |
| Product with description `"alphabet"` but name `"Watch"` | `"alpha"` | `[]` *(description is NOT matched)* |

## Backward compatibility

- Other existing clients of `SearchProducts` (the loadgenerator hits ListProducts/GetProduct only — `searchProducts` is not currently called by any client in this repo, per a `Grep` of `SearchProducts` outside `genproto/`) will see a strictly-smaller (or equal) result set after the description match is dropped. No client currently depends on the description-broadening behaviour.
- The proto file itself is unchanged, so no regenerated code rolls out to other services.
