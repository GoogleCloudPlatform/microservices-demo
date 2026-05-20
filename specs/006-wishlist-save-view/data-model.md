# Data Model: Wishlist — Save a Product for Later and View the Saved List

## Entities

### Wishlist

A session-scoped, ordered collection of saved products. Exists only for the lifetime of the browser session (tab close or cookie expiry clears it).

| Attribute | Type | Description |
|-----------|------|-------------|
| items | []WishlistItem | Ordered list of saved products, most-recently-saved first |

**Invariants**:
- No duplicate product IDs. Attempting to save an already-saved product is a no-op.
- Maximum size is not enforced (assumption: sessions with >50 items are not a primary concern).

**Storage**: Browser cookie `shop_wishlist`. Value is a pipe-delimited string of product IDs, e.g. `OLJCESPC7Z|L9ECAV44F0|2ZYFJ3GM2N`. Empty wishlist = absent or empty cookie value.

---

### WishlistItem

A snapshot of a product at save time. Resolved fresh from the product catalogue on every wishlist page load (no stale data stored in the cookie).

| Attribute | Type | Source |
|-----------|------|--------|
| ID | string | Product catalogue |
| Name | string | Product catalogue |
| Picture | string (URL path) | Product catalogue |
| PriceUsd | Money | Product catalogue → converted to user currency at render time |

---

## Cookie Schema

| Cookie name | Format | Lifetime | Set by |
|-------------|--------|----------|--------|
| `shop_wishlist` | `<id1>\|<id2>\|...` (pipe-delimited product IDs) | `cookieMaxAge` (48 h) | `saveToWishlistHandler` on POST `/wishlist` |

**Notes**:
- IDs are raw product IDs from the product catalogue (same format as `shop_recently-viewed`).
- Cookie expires after 48 hours of inactivity (matches `cookieMaxAge`), satisfying the "session-only" intent. Closing the tab without clearing cookies will let the wishlist survive a re-open within 48 h — this is consistent with how `shop_recently-viewed` behaves and is acceptable per the Assumptions in the spec.

---

## State Transitions

```
Product not in wishlist
        │
        │  POST /wishlist (product_id)
        ▼
Product in wishlist (cookie updated, redirect to /product/{id}?saved=1)
        │
        │  New browser session / cookie expiry
        ▼
Product not in wishlist (fresh session)
```

---

## Relationships to Existing Entities

- **WishlistItem → Product**: resolved via `fe.getProduct(ctx, id)` — same RPC used by `getRecentlyViewedProducts`.
- **Wishlist → Session**: tied to `shop_session-id` cookie lifetime (48 h); no explicit link in the data, just co-resident browser cookies.
