# Ground truth fix — bug_06_cart_quantity_overwritten

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/cartservice/src/cartstore/RedisCartStore.cs`

## Exact change

```diff
--- a/src/cartservice/src/cartstore/RedisCartStore.cs
+++ b/src/cartservice/src/cartstore/RedisCartStore.cs
@@ public async Task AddItemAsync(string userId, string productId, int quantity)
                 var existingItem = cart.Items.SingleOrDefault(i => i.ProductId == productId);
                 if (existingItem == null)
                 {
                     cart.Items.Add(new Hipstershop.CartItem { ProductId = productId, Quantity = quantity });
                 }
                 else
                 {
-                    existingItem.Quantity = quantity;
+                    existingItem.Quantity += quantity;
                 }
```

## Why this is correct
`AddItemAsync` is called once per "Add To Cart" action with just the quantity
selected on that single action, not the shopper's intended running total.
Accumulating (`+=`) onto whatever quantity is already stored for that product
correctly reflects "the shopper now has N more of this item than before,"
matching the behavior of every other cart implementation in this repo
(`SpannerCartStore.cs`, `AlloyDBCartStore.cs` already do the same `+=`).
No other file needs to change.
