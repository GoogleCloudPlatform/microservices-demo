# Ground truth — bug_05_adservice_category_mismatch

## Bug status
**Planted and currently live in source.** File already modified:
`src/adservice/src/main/java/hipstershop/AdService.java`, lines 186 and 188.

## Root cause (plain English)
The ad shown on the Loafers product page (a "footwear" item) advertises a
Tank Top instead of Loafers, and conversely the Tank Top product page (a
"clothing" item) now advertises Loafers. The ads for these two categories
have been swapped.

## Root cause (technical)
`AdService.createAdsMap()` builds a lookup table from product category string
→ list of ads for that category:

```diff
  return ImmutableListMultimap.<String, Ad>builder()
-     .putAll("clothing", loafers)
+     .putAll("clothing", tankTop)
      .putAll("accessories", watch)
-     .putAll("footwear", tankTop)
+     .putAll("footwear", loafers)
      .putAll("hair", hairdryer)
```

The frontend calls `adChooser.choose(product.getCategoriesList())` with the
*viewed* product's own categories (`ProductController.java`), so a footwear
page requests the `"footwear"` bucket and a clothing page requests
`"clothing"`. With the two `.putAll(...)` lines swapped, the `"footwear"` key
now maps to the Tank Top ad and the `"clothing"` key maps to the Loafers ad —
the category labels and the ad content built under them no longer agree.

## Why this is hard to spot
`createAdsMap()` is one long builder chain with six categories and the ad
variables are declared well above it, so matching each `putAll(category, ad)`
call back to the right product requires cross-referencing the ad's own
`redirectUrl`/`text` (declared 30+ lines earlier) against the category string
on that specific line — a swap between two adjacent, same-shaped lines reads
as entirely plausible on a quick scan, and the code compiles and runs with no
errors either way.
