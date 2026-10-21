# Ground truth fix — bug_05_adservice_category_mismatch

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/adservice/src/main/java/hipstershop/AdService.java`

## Exact change

The bug swapped the ad assigned to each of these two categories. The fix
restores the original pairing:

```diff
--- a/src/adservice/src/main/java/hipstershop/AdService.java
+++ b/src/adservice/src/main/java/hipstershop/AdService.java
@@ private static ImmutableListMultimap<String, Ad> createAdsMap() {
     return ImmutableListMultimap.<String, Ad>builder()
-        .putAll("clothing", loafers)
+        .putAll("clothing", tankTop)
         .putAll("accessories", watch)
-        .putAll("footwear", tankTop)
+        .putAll("footwear", loafers)
         .putAll("hair", hairdryer)
```

## Why this is correct
`tankTop`'s `redirectUrl` points at `/product/66VCHSJNUP` (Tank Top, a
clothing item) and `loafers`'s `redirectUrl` points at `/product/L9ECAV7KIM`
(Loafers, a footwear item). Mapping `"clothing" → tankTop` and `"footwear" →
loafers` makes the category key and the ad's own target product agree again,
so browsing a footwear product requests the `"footwear"` ads and correctly
gets the Loafers ad, and vice versa for clothing.
