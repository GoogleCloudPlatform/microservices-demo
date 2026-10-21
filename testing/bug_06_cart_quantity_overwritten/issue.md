# Ground truth — bug_06_cart_quantity_overwritten

## Bug status
**Planted and currently live in source.** File already modified:
`src/cartservice/src/cartstore/RedisCartStore.cs`, line 57.

## Root cause (plain English)
A shopper who adds 2 Sunglasses to their cart, keeps browsing, then adds 1
more Sunglasses later ends up with only **1** Sunglasses in their cart, not
3. The second "Add To Cart" wipes out the quantity from the first one instead
of adding to it.

## Root cause (technical)
`RedisCartStore.AddItemAsync` already has an explicit branch for "this
product is already in the cart" — it's just doing the wrong arithmetic in
that branch:

```diff
  var existingItem = cart.Items.SingleOrDefault(i => i.ProductId == productId);
  if (existingItem == null)
  {
      cart.Items.Add(new Hipstershop.CartItem { ProductId = productId, Quantity = quantity });
  }
  else
  {
-     existingItem.Quantity = quantity;
+     existingItem.Quantity += quantity;
  }
```

With a plain assignment (`=`) instead of an increment (`+=`), every repeat
"Add To Cart" for a product already in the cart **replaces** the stored
quantity with whatever quantity was just selected on the product page,
instead of adding to what's already there. Two separate adds of quantity 2
then quantity 1 leave the cart holding just 1, not 3.

## Why this is hard to spot
The code already correctly distinguishes "new item" vs "item already in
cart" — the bug isn't in the branching logic, which looks entirely sound,
it's in a single operator inside the branch that's clearly meant to handle
exactly this accumulation case. A test that only adds each product once
(the far more common manual-testing pattern) will never trigger this at all;
it only shows up when the *same* product is added across two or more
separate "Add To Cart" actions.
