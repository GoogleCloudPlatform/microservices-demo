# Ground truth — bug_08_productsearch_case_sensitive

## Bug status
**Planted and currently live in source.** File already modified:
`src/productcatalogservice/product_catalog.go`, line 65.

## Root cause (plain English)
Typing an all-lowercase search term — e.g. "loafers" — into the shop's
search box returns **zero results**, even though a product called "Loafers"
is right there in the catalog. Searching with the exact capitalization
"Loafers" works fine; only a lowercase (or otherwise differently-cased) query
fails.

## Root cause (technical)
`SearchProducts` matches a query against both the product name and
description, lower-casing both sides of each comparison so the match is
case-insensitive. The product-name comparison lost its lower-casing on one
side:

```diff
  for _, product := range p.parseCatalog() {
-     if strings.Contains(product.Name, strings.ToLower(req.Query)) ||
+     if strings.Contains(strings.ToLower(product.Name), strings.ToLower(req.Query)) ||
          strings.Contains(strings.ToLower(product.Description), strings.ToLower(req.Query)) {
          ps = append(ps, product)
      }
  }
```

`product.Name` is left in its original catalog casing ("Loafers"), while
`req.Query` is still lower-cased ("loafers"). `strings.Contains("Loafers",
"loafers")` is `false` — Go string comparison is byte-exact, so a capital `L`
never matches a lowercase `l`. The description-match clause can't rescue the
search either, because "Loafers" the product's description ("A neat addition
to your summer wardrobe.") never actually contains the word "loafers."

## Why this is hard to spot
Three of the four `ToLower(...)` calls in this condition are still present
and correct — only one, on `product.Name`, is missing — so a quick visual
scan of the line sees "lots of `ToLower` calls, looks case-insensitive" and
moves on. The bug is also query-dependent: any search whose term also
happens to appear (in lowercase) inside the matching product's *description*
still works, because the description-match clause is untouched and correctly
lower-cases both sides — so this only reproduces for products, like Loafers,
whose name doesn't also appear in their own description text.
