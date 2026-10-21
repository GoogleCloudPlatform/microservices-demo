# Ground truth fix — bug_03_recommendations_always_empty

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/recommendationservice/recommendation_server.py`

## Exact change

```diff
--- a/src/recommendationservice/recommendation_server.py
+++ b/src/recommendationservice/recommendation_server.py
@@ def ListRecommendations(self, request, context):
         product_ids = [x.id for x in cat_response.products]
-        filtered_products = list(set(request.product_ids)-set(product_ids))
+        filtered_products = list(set(product_ids)-set(request.product_ids))
         num_products = len(filtered_products)
```

## Why this is correct
`product_ids` is every product ID in the catalog; `request.product_ids` is the
set of IDs the caller wants excluded (the shopper's current cart contents).
Subtracting the exclude-list from the full catalog (`set(product_ids) -
set(request.product_ids)`) yields exactly what the function's own name
promises: every catalog product that is NOT already in the cart. With the
operands swapped back, `num_products` is populated again, `random.sample`
has a real range to draw from, and the "Other products you might like"
section renders a normal, non-empty list.
