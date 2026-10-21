# Ground truth — bug_03_recommendations_always_empty

## Bug status
**Planted and currently live in source.** File already modified:
`src/recommendationservice/recommendation_server.py`, line 75.

## Root cause (plain English)
The "Other products you might like" section on every product page is always
empty, no matter what's in the catalog or the shopper's cart. This isn't a
display problem — the recommendation service itself is returning zero product
IDs.

## Root cause (technical)
`ListRecommendations` is supposed to recommend products from the catalog that
are **not already in the shopper's cart**. It does this with a Python set
difference: "all catalog product IDs" minus "the product IDs already in the
cart". The two operands of that subtraction were swapped:

```diff
- filtered_products = list(set(request.product_ids) - set(product_ids))
+ filtered_products = list(set(product_ids) - set(request.product_ids))
```

`set(request.product_ids)` is the (small) list of product IDs already in the
cart; `set(product_ids)` is the (large) full catalog. Subtracting the full
catalog *from* the cart IDs, instead of the other way around, means the result
is (almost always) empty: a cart ID that's already a member of the catalog
set has nothing left over once the catalog set is removed from it. In
practice this collapses to an empty list on virtually every call, which is why
the section is empty for every product and every cart state, not just some.

## Why this is hard to spot
The code still runs without error — it doesn't crash, throw, or log anything
unusual, it just silently returns an empty (or near-empty) list every time.
Both operands are named plausibly (`product_ids`, `request.product_ids`), so a
quick read doesn't reveal which one is "the cart" and which is "the catalog"
without cross-referencing the surrounding lines (`cat_response =
product_catalog_stub.ListProducts(...)` a few lines above, and the gRPC
request schema) to see that `request.product_ids` is the caller-supplied
exclude-list, not the thing to subtract from.
