# Research: Wishlist — Save a Product for Later and View the Saved List

## Session / Persistence Mechanism

**Decision**: Store the wishlist in a browser cookie (`shop_wishlist`), using pipe-delimited product IDs — identical in structure to the existing `shop_recently-viewed` cookie.

**Rationale**: The codebase already uses this exact pattern for recently-viewed. `recentlyViewedFromCookie` / `updateRecentlyViewed` in `handlers.go` are the direct model. No new datastore or service is needed, and the approach is naturally session-scoped (lost when the tab closes / cookie expires).

**Alternatives considered**:
- `gorilla/sessions` in-memory store: not used anywhere in the project; adds a dependency.
- Browser `localStorage` (JavaScript): would require JS mutation of state and a separate fetch to resolve product details — inconsistent with the server-rendered pattern.
- Cart service (Redis-backed): would persist across sessions and require a new service call, violating the epic constraint.

---

## Save Confirmation (inline feedback)

**Decision**: After a successful POST to `/wishlist`, redirect back to the product detail page with a `?saved=1` query parameter. The product template renders a dismissible banner when that parameter is present.

**Rationale**: All other write actions in the frontend (add to cart, set currency) use POST → redirect. No JavaScript is used for state mutation. A query-param banner follows the same server-rendered pattern without adding JS.

**Alternatives considered**:
- Flash cookie: works but requires writing + consuming a short-lived cookie — more moving parts.
- AJAX / fetch: inconsistent with the existing zero-JS-mutation pattern in the codebase.

---

## "Already saved" state on PDP

**Decision**: `productHandler` reads the wishlist cookie and passes `in_wishlist bool` to the template. The template renders a toggled "Saved ✓" label instead of the "Save for later" button when `in_wishlist` is true.

**Rationale**: Consistent with how `cart_size` is computed from a cookie/RPC result and passed per-handler. No client-side state needed.

---

## Wishlist Header Icon

**Decision**: Use the Google Symbols icon font (already loaded in `header.html`) with the `bookmarks` symbol. Add a `<a href="/wishlist">` link immediately before the existing cart icon `<a>` tag, using the same `cart-link` class for consistent spacing. Show a count badge (`wishlist_size`) using the same `cart-size-circle` pattern.

**Rationale**: The font is already in the `<head>`. Adding an SVG file is unnecessary when a symbol glyph matches the aesthetic. The `cart-size-circle` pattern is already styled in `styles.css`.

**Alternatives considered**:
- New SVG file: works but requires a new static asset; the symbol font is already present.
- FontAwesome or other icon lib: not used in the project.

---

## Wishlist Size in Header (all pages)

**Decision**: Compute `wishlist_size` inside `injectCommonTemplateData` directly from the request cookie — no RPC call required. This makes it available on every rendered page without modifying each handler individually.

**Rationale**: The wishlist is a pure cookie read. Unlike `cart_size` (which requires a cart service RPC and is passed per-handler), `wishlist_size` is free to compute and belongs naturally alongside `session_id` and `user_currency` in the common data injector.

---

## Deduplication

**Decision**: Enforce deduplication in the save helper function (same pattern as `updateRecentlyViewed`). If the product is already in the wishlist, the save is a no-op and the redirect still returns `?saved=1` with a "already saved" message.

**Rationale**: FR-004 requires no duplicates. Server-side enforcement is simpler and more reliable than relying on template state.

---

## Files Changed

| File | Change |
|------|--------|
| `src/frontend/main.go` | Add `cookieWishlist` constant; register `GET /wishlist` and `POST /wishlist` routes |
| `src/frontend/handlers.go` | Add `viewWishlistHandler`, `saveToWishlistHandler`, `wishlistFromCookie`, `updateWishlist`; update `injectCommonTemplateData` with `wishlist_size`; update `productHandler` with `in_wishlist` |
| `src/frontend/templates/header.html` | Add wishlist icon link before cart icon |
| `src/frontend/templates/product.html` | Add "Save for later" form; show confirmation banner on `?saved=1` |
| `src/frontend/templates/wishlist.html` | New template — wishlist page |
