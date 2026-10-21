# Ground truth — bug_07_multiplyslow_undercounts_quantity

## Bug status
**Planted and currently live in source.** File already modified:
`src/frontend/src/main/java/hipstershop/frontend/money/Money.java`, line 102.

## Root cause (plain English)
Any time a shopper adds **2 or more** of the same item, every subtotal that
includes that line — the cart page, the order summary, and the final total —
is short by exactly one unit's price. For 3 Watches at $109.99 each, the
cart shows $219.98 (2 × $109.99) instead of the correct $329.97 (3 × $109.99).

## Root cause (technical)
`Money.multiplySlow(m, n)` computes `n * m` the same way the original Go
frontend did — by repeated addition, starting from one copy of `m` and adding
`m` again `n-1` more times. The loop's continuation condition was changed
from `n > 1` to `n > 2`:

```diff
  public static Hipstershop.Money multiplySlow(Hipstershop.Money m, long n) {
      Hipstershop.Money out = m;
-     while (n > 2) {
+     while (n > 1) {
          out = sum(out, m);
          n--;
      }
      return out;
  }
```

For `n=3`: starting at `out=m` (1×), the loop only runs while `n>2`, so it
adds once (`out=2×m`, `n=2`) and then stops — one addition short of the three
copies needed. For `n=2`, the loop condition `n>2` is false immediately, so
the result stays at `out=m` (1×) instead of `2×m`. Every quantity ≥ 2 is
under-multiplied by exactly one unit price; quantity 1 (the single most common
manual test case) is unaffected, which is exactly why this slipped through.

## Why this is hard to spot
`multiplySlow` is a single shared utility called from several unrelated call
sites — `CheckoutController` (order totals), `CartController` (cart subtotal
preview), `CheckoutServiceImpl`'s Java port isn't involved here, but the
*symptom* shows up on multiple pages at once (cart, checkout, order
confirmation), which makes it look at first like three separate display bugs
rather than one shared arithmetic bug. The off-by-one only manifests at
quantity ≥ 2, so it's invisible in any test that only orders a single unit of
each product.
