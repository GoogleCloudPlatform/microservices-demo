# Contract — HTTP `GET /search`

**Service**: `frontend`
**Route**: `GET /search`
**Handler**: `searchHandler` in `src/frontend/handlers.go:122`
**Status**: existing on the wire; **semantics tightened by this slice** — no new route, no new query parameters.

## Request

| Aspect | Contract |
|---|---|
| Method | `GET` |
| Path | `/search` |
| Query parameters | `q` — the user-typed search string. Optional. Other query parameters (`?currency=`, etc.) are inherited from existing storefront middleware and unaffected by this slice. |
| Headers | Standard storefront cookies (session id, currency, etc.). No new headers. |

## Response

| Status | Body | When |
|---|---|---|
| `200 OK` | Rendered `search.html` template with header, results section, footer. | `q` is absent, empty, whitespace-only, or matches >= 0 products. |
| `500 Internal Server Error` | Rendered `error.html` template. | The downstream `SearchProducts` RPC fails (e.g. `productcatalogservice` is unreachable). **Existing behaviour, retained.** A soft-degradation alternative is listed in `plan.md` as an optional follow-up. |

## Rendered page contract

The `search.html` template rendered at `200 OK` MUST exhibit:

| Condition | Rendered behaviour |
|---|---|
| `q` is absent / empty / whitespace-only | Page shows the global header (including the search form), the title "Search" (or equivalent), and a prompt to type a query. **No backend call is made.** Satisfies FR-010. |
| `q` is non-empty and matches one or more products | Page shows the global header, a heading "Search results for &ldquo;{q}&rdquo;", a count line, and a card per matching product (image, name, price, link to `/product/{id}`). Satisfies FR-005. |
| `q` is non-empty and matches zero products | Page shows the global header, an explicit empty-state message (e.g. "No products found for &ldquo;{q}&rdquo;"), and helpful guidance. Satisfies FR-006. **This branch is new in this slice (template edit).** |

## Header form contract (unchanged)

The header form in `templates/header.html` MUST:

- Be rendered on every storefront page that includes `{{ template "header" . }}`. Currently: all pages except `error.html` (intentional). Satisfies FR-001 and SC-004.
- Submit `GET` to `/search` with `q` as the input name.
- Preserve the current query in the input on the search results page (`value="{{ $.query }}"`).

## Inputs the frontend MUST NOT send to the backend

- `q == ""` after trimming whitespace — frontend short-circuits per FR-010.
- Any additional fields on `SearchProductsRequest` — there aren't any in this slice.

## Out of contract (explicitly)

- **No `/api/search` JSON endpoint.** This slice serves rendered HTML only. No new endpoint for JS consumers, no fetch-based as-you-type, no autocomplete.
- **No new query parameters** (`?limit=`, `?offset=`, `?category=`). The route accepts `q` only (plus inherited storefront params).
- **No new headers**, cookies, CSRF tokens, etc.
- **No POST variant.** Search is a `GET` action — bookmarkable, shareable, idempotent.
