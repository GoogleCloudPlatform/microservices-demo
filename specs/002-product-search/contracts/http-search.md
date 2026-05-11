# Contract: Frontend HTTP `GET /search`

**Status**: NEW. Owned by `src/frontend`.

## Route

```text
GET {baseUrl}/search?q={query}
```

Registered in `src/frontend/main.go` next to the other `r.HandleFunc(...)` lines using `gorilla/mux`, methods `GET, HEAD`.

## Request

| Parameter | Location | Type | Required | Notes |
|---|---|---|---|---|
| `q` | URL query string | `string` | Yes (effectively) | The shopper's raw search input. May contain leading/trailing whitespace; the handler trims it. |

No request body. No custom headers.

## Handler behaviour

```text
q_raw   := r.URL.Query().Get("q")
q       := strings.TrimSpace(q_raw)

if q == "":
    return 302 redirect to {baseUrl}/

resp, err := fe.searchProducts(ctx, q)
if err != nil:
    return existing renderHTTPError() pattern (HTTP 500 via error.html)

render "search" template with:
    - query   = q
    - results = resp.GetResults()
    - plus the usual page context (currencies, session, baseUrl, etc.)
      established by the existing handlers
```

## Response status codes

| Code | Trigger |
|---|---|
| `200 OK` | At least one match, OR zero matches but `q` was non-empty (renders the "no results" panel inside `search.html`). |
| `302 Found` | `q` is empty after trimming. `Location: {baseUrl}/`. |
| `500 Internal Server Error` | Downstream gRPC error from `SearchProducts`. Renders the existing `error.html` template, same as other handlers. |

The response is HTML rendered from `templates/search.html`. No JSON contract is exposed for v1 (out of scope per spec).

## Template binding

`search.html` receives (at minimum) the same base context as `home.html` plus:

| Key | Type | Meaning |
|---|---|---|
| `query` | `string` | Trimmed query, echoed back into the search box `value=` attribute and into the "no results" message. |
| `results` | `[]*pb.Product` | Products to render as cards. Empty slice triggers the "no results" panel. |

## Search box markup (in `templates/header.html`)

The shared header gains, inside the existing `sub-navbar` container:

```html
<form class="search-form" action="{{ $.baseUrl }}/search" method="GET" role="search">
  <input type="text" name="q" placeholder="Search products"
         aria-label="Search products" value="{{ $.searchQuery }}">
  <button type="submit" aria-label="Submit search">…</button>
</form>
```

`{{ $.searchQuery }}` is supplied by the `searchHandler`; other handlers omit it (template renders an empty `value`).

## Out-of-scope for v1

- JSON / AJAX search-as-you-type endpoint.
- Pagination, sort, filter parameters.
- Saved searches, recent searches, query history.
- Spelling correction / suggestions.
