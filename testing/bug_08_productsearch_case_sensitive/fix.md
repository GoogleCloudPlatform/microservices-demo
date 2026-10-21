# Ground truth fix — bug_08_productsearch_case_sensitive

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/productcatalogservice/product_catalog.go`

## Exact change

```diff
--- a/src/productcatalogservice/product_catalog.go
+++ b/src/productcatalogservice/product_catalog.go
@@ func (p *productCatalog) SearchProducts(ctx context.Context, req *pb.SearchProductsRequest) (*pb.SearchProductsResponse, error) {
     for _, product := range p.parseCatalog() {
-        if strings.Contains(product.Name, strings.ToLower(req.Query)) ||
+        if strings.Contains(strings.ToLower(product.Name), strings.ToLower(req.Query)) ||
             strings.Contains(strings.ToLower(product.Description), strings.ToLower(req.Query)) {
             ps = append(ps, product)
         }
     }
```

## Why this is correct
Lower-casing `product.Name` before comparing it against the already-lowered
`req.Query` makes the comparison case-insensitive on both sides again,
matching the description-match clause right next to it. "loafers" (lowered
query) now matches "loafers" (lowered "Loafers"), so the search correctly
returns the Loafers product regardless of how the shopper capitalizes their
search term. No other file needs to change.
