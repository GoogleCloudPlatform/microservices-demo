# Quickstart: Recently Viewed Strip

**Feature**: `specs/004-recently-viewed-strip`
**Date**: 2026-05-20

---

## Files to change

| File | Change |
|------|--------|
| `src/frontend/handlers.go` | Update `productHandler` to read/write `shop_recently_viewed` cookie and pass resolved products to template |
| `src/frontend/templates/product.html` | Add `{{ template "recently_viewed" $ }}` conditional below the recommendations block |
| `src/frontend/templates/recently_viewed.html` | New partial template for the strip (mirrors `recommendations.html`) |
| `src/frontend/static/styles.css` | Add `.recently-viewed` section styles (mirrors `.recommendations`) |

No other files need to change. No new services, protos, manifests, or dependencies.

---

## Cookie constant to add (handlers.go)

```go
cookieRecentlyViewed = "shop_recently_viewed"
```

Add alongside the existing `cookieCurrency` and `cookieSessionID` constants in `main.go`.

---

## Handler logic to add (productHandler, handlers.go)

Before the existing `recommendations` call, read and update the cookie:

```go
// Read existing list
recentlyViewedIDs := recentlyViewedFromCookie(r)
// Update cookie (prepend current, dedup, cap at 5)
updatedIDs := updateRecentlyViewed(recentlyViewedIDs, id)
http.SetCookie(w, &http.Cookie{
    Name:   cookieRecentlyViewed,
    Value:  strings.Join(updatedIDs, "|"),
    MaxAge: cookieMaxAge,
})
// Fetch products for strip (excludes current product — updatedIDs[1:])
recentlyViewed, err := fe.getRecentlyViewedProducts(r.Context(), updatedIDs[1:])
if err != nil {
    log.WithField("error", err).Warn("failed to get recently viewed products")
}
```

Add `"recently_viewed": recentlyViewed` to the template data map.

---

## New helper functions (handlers.go or a new recently_viewed.go)

```go
// recentlyViewedFromCookie parses the cookie into a slice of product IDs.
func recentlyViewedFromCookie(r *http.Request) []string {
    c, err := r.Cookie(cookieRecentlyViewed)
    if err != nil || c.Value == "" {
        return nil
    }
    return strings.Split(c.Value, "|")
}

// updateRecentlyViewed prepends id, deduplicates, and caps at 5.
func updateRecentlyViewed(existing []string, id string) []string {
    seen := map[string]bool{}
    result := []string{id}
    seen[id] = true
    for _, v := range existing {
        if !seen[v] {
            result = append(result, v)
            seen[v] = true
        }
    }
    if len(result) > 5 {
        result = result[:5]
    }
    return result
}

// getRecentlyViewedProducts fetches *pb.Product for each ID.
func (fe *frontendServer) getRecentlyViewedProducts(ctx context.Context, ids []string) ([]*pb.Product, error) {
    var products []*pb.Product
    for _, id := range ids {
        p, err := fe.getProduct(ctx, id)
        if err != nil {
            return products, err  // return what we have so far
        }
        products = append(products, p)
    }
    return products, nil
}
```

---

## Template: recently_viewed.html

```html
{{define "recently_viewed"}}
<section class="recently-viewed">
  <div class="container">
    <h2>Recently Viewed</h2>
    <div class="row">
      {{range .recently_viewed}}
      <div class="col-md-3">
        <a href="{{$.baseUrl}}/product/{{.Id}}">
          <img alt="{{.Name}}" src="{{$.baseUrl}}{{.Picture}}" loading="lazy">
        </a>
        <h5>{{.Name}}</h5>
      </div>
      {{end}}
    </div>
  </div>
</section>
{{end}}
```

---

## product.html: where to insert the strip

Add after the existing recommendations block (around line 78):

```html
{{if $.recently_viewed}}
  {{template "recently_viewed" $}}
{{end}}
```

---

## How to run locally (Skaffold)

```bash
# From repo root — hot-reloads the frontend on file changes
skaffold dev --port-forward
# Open http://localhost:80, browse a few products, return to any product page
```

## Manual test sequence

1. Open the shop fresh (no `shop_recently_viewed` cookie).
2. Navigate to Product A → no strip should appear.
3. Navigate to Product B → strip shows Product A.
4. Navigate to Product C → strip shows B, A (most recent first).
5. Navigate back to Product A → strip shows C, B (A is current; not in strip).
6. View 6+ products → strip never shows more than 5 entries.
