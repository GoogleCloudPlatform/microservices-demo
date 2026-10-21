# Ground truth fix — bug_07_multiplyslow_undercounts_quantity

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/frontend/src/main/java/hipstershop/frontend/money/Money.java`

## Exact change

```diff
--- a/src/frontend/src/main/java/hipstershop/frontend/money/Money.java
+++ b/src/frontend/src/main/java/hipstershop/frontend/money/Money.java
@@ public static Hipstershop.Money multiplySlow(Hipstershop.Money m, long n) {
     Hipstershop.Money out = m;
-    while (n > 2) {
+    while (n > 1) {
         out = sum(out, m);
         n--;
     }
     return out;
```

## Why this is correct
Starting from one copy of `m` (`out = m`), the loop needs to add `m` exactly
`n - 1` more times to reach `n` total copies. `while (n > 1)` does exactly
that: for `n=1` it never runs (1 copy, correct); for `n=2` it runs once (2
copies, correct); for `n=3` it runs twice (3 copies, correct). This matches
the Go frontend's original `multiplySlow` this code is a direct port of.
Restoring the condition fixes the subtotal everywhere `multiplySlow` is
called from (cart page, checkout page, order confirmation) with a single
one-line change — no other file needs to change.
