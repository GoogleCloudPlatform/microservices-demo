# Quickstart: Wishlist Feature (AIP-159)

## What was built

A session-scoped "Save for later" wishlist for Online Boutique. Shoppers can save products from the product detail page, view their saved list at any time via a header icon, and the list is automatically cleared when the browser session ends.

## Where to look

| What | Where |
|------|-------|
| Cookie constants | `src/frontend/main.go` — `cookieWishlist` |
| Wishlist helpers | `src/frontend/handlers.go` — `wishlistFromCookie`, `updateWishlist` |
| Save handler | `src/frontend/handlers.go` — `saveToWishlistHandler` |
| View handler | `src/frontend/handlers.go` — `viewWishlistHandler` |
| Header icon | `src/frontend/templates/header.html` — before the cart `<a>` tag |
| Save button + confirmation | `src/frontend/templates/product.html` |
| Wishlist page | `src/frontend/templates/wishlist.html` |

## How to run locally

```sh
# From repo root — start just the frontend (adjust addresses to match your local setup)
cd src/frontend
go run .
```

The wishlist is fully exercised without any backend changes. You can test it with a running `productcatalogservice` (and the other required services) per the project's existing dev setup.

## How to verify

1. Open any product detail page (`/product/{id}`).
2. Click **Save for later** → confirm the inline "Saved to your wishlist" banner appears.
3. Click the list icon in the header → confirm the wishlist page shows the saved product with name, image, and price.
4. Return to the same product detail page → confirm the button now shows **Saved ✓** and clicking it again does not add a duplicate.
5. Open a new browser tab (new session) → confirm the wishlist is empty.

## Key patterns to follow when extending

- **Cookie format**: pipe-delimited product IDs, `MaxAge: cookieMaxAge`. See `wishlistFromCookie` / `updateWishlist` — mirrors `recentlyViewedFromCookie` / `updateRecentlyViewed`.
- **Template data**: All wishlist template data goes through `injectCommonTemplateData` (for `wishlist_size`) or is passed per-handler (for `items`, `in_wishlist`, `just_saved`).
- **Confirmation pattern**: POST → redirect with `?saved=1` query param → template renders banner. No JavaScript required.
- **Product resolution**: Use `fe.getProduct` + `fe.convertCurrency` per item, same as `viewCartHandler`.
