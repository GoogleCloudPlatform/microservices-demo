# HTTP Route Contracts: Wishlist Feature

These routes extend the existing `gorilla/mux` router in `src/frontend/main.go`.

---

## GET /wishlist

**Purpose**: Render the wishlist view page.

**Handler**: `viewWishlistHandler`

**Request**: No body, no required query parameters.

**Behaviour**:
1. Read `shop_wishlist` cookie → parse into ordered product ID slice.
2. For each ID, call `fe.getProduct` and `fe.convertCurrency` (same as `viewCartHandler`).
3. Render `wishlist` template with product list, currency, and `cart_size` / `wishlist_size`.
4. If cookie is absent or empty, render with an empty item list (empty-state message shown by template).

**Response**: `200 OK` — HTML page.

**Template data keys**:

| Key | Type | Description |
|-----|------|-------------|
| `items` | `[]wishlistItemView` | Resolved product list with converted price |
| `wishlist_size` | `int` | Count of items in the wishlist |
| `cart_size` | `int` | Count of items in cart (for header badge) |
| `show_currency` | `bool` | `true` |
| `currencies` | `[]string` | Available currencies |

---

## POST /wishlist

**Purpose**: Save a product to the wishlist.

**Handler**: `saveToWishlistHandler`

**Request body** (form-encoded):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_id` | string | yes | ID of the product to save |
| `redirect_url` | string | no | URL to redirect to after save (defaults to `/product/{product_id}`) |

**Behaviour**:
1. Validate `product_id` is non-empty.
2. Read `shop_wishlist` cookie.
3. Add product ID if not already present (deduplicate).
4. Write updated `shop_wishlist` cookie (`MaxAge: cookieMaxAge`).
5. Redirect to `redirect_url` (or `/product/{product_id}`) with `?saved=1` appended.

**Response**: `302 Found` — redirect to product detail page.

**Error**: `400 Bad Request` if `product_id` is empty.

---

## Modified: GET /product/{id}

**Purpose** (existing route, extended): Product detail page now accepts a `saved` query parameter.

**Query parameter**:

| Parameter | Value | Effect |
|-----------|-------|--------|
| `saved` | `1` | Template renders an inline confirmation banner ("Saved to your wishlist") |

**Additional template data keys added**:

| Key | Type | Description |
|-----|------|-------------|
| `in_wishlist` | `bool` | Whether this product is already in the wishlist |
| `just_saved` | `bool` | Whether `?saved=1` is present (drives inline confirmation) |

---

## Cookie Contract

| Cookie | Written by | Read by | Format |
|--------|-----------|---------|--------|
| `shop_wishlist` | `POST /wishlist` | `GET /wishlist`, `GET /product/{id}`, `injectCommonTemplateData` | pipe-delimited product IDs |
