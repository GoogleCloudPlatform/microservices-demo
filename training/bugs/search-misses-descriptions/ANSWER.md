# Trainer cheat sheet — search-misses-descriptions

**Service:** `productcatalogservice` (Go)
**File:** `src/productcatalogservice/product_catalog.go`
**Function:** `SearchProducts()`, line ~65.

## What the bug is

`SearchProducts` used to match against both `product.Name` and
`product.Description`. The description-matching half of the OR was
removed. So queries that only appear in descriptions ("modern",
"summer", "vintage", "comfortable") return zero results, while queries
that match a product name ("watch", "tank") still work. The pattern in
the customer's report — "some queries work, others don't, depending on
what kind of word it is" — is the diagnostic.

## What a good triage ticket looks like

- **Steps to reproduce:** in the search box, query "modern" → no results.
  "watch" → 1 result. The split is words-that-appear-in-product-names
  (work) vs. words-that-only-appear-in-descriptions (fail).
- **Suspected area:** `productcatalogservice`'s `SearchProducts` RPC.
  The shape of the failure (matches a *subset* of the product's
  searchable text) points at a missing field in the search predicate
  rather than a tokenizer or indexer problem.
- **Severity rationale:** not a checkout-blocker, but discoverability is
  measurably worse — likely shows up in conversion data this week. P2.

## The actual fix

Restore the second clause of the OR so descriptions are matched again.
