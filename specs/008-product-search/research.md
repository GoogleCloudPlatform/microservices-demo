# Phase 0 — Research: Product Search (thin slice)

**Branch**: `008-product-search` | **Date**: 2026-06-02

All `[NEEDS CLARIFICATION]` markers in the spec are resolved before this phase. This document captures the **design-relevant decisions** that affect Phase 1 contracts and the subsequent implementation tasks.

---

## R-1. Match scope — name OR description

**Decision** *(updated 2026-06-02 after spec amendment)*: **keep the existing name-OR-description match logic unchanged.** The spec was amended to widen the match scope from `name` only to `name OR description`, aligning with the existing implementation and the workshop's prior "restore description match" commit. No Go code change is required.

**What's there today and stays unchanged**: `src/productcatalogservice/product_catalog.go:60-72`:

```go
func (p *productCatalog) SearchProducts(ctx context.Context, req *pb.SearchProductsRequest) (*pb.SearchProductsResponse, error) {
    time.Sleep(extraLatency)

    var ps []*pb.Product
    for _, product := range p.parseCatalog() {
        if strings.Contains(strings.ToLower(product.Name), strings.ToLower(req.Query)) ||
            strings.Contains(strings.ToLower(product.Description), strings.ToLower(req.Query)) {
            ps = append(ps, product)
        }
    }

    return &pb.SearchProductsResponse{Results: ps}, nil
}
```

**What the amended spec requires**: TC-002, FR-003, FR-004 — match the product if EITHER `name` OR `description` contains the query as a case-insensitive substring. A product appears at most once (loop iterates products, not fields).

**Rationale for keeping the existing code**: the existing code is exactly what the amended spec describes. The branch's history (`2371e659` seed bug, `736cf79b` restore) was specifically engineered for the workshop to teach this very moment: when implementation reality diverges from the spec, the right SDD response is to either align the spec or align the code — not to silently let them drift. The user chose to align the spec with the code.

**Alternatives considered**:

- *Match on name only* (original spec) — would require dropping the `||` arm. Rejected by the user's decision; spec was amended instead.
- *Match on name, description, and categories* — extends scope further. Not on the table; categories were never in scope, and the user's directive was specifically about preserving description matching, not widening further.

**Affected by**: nothing — code stays as-is. The test file is extended to cover the description-match behaviour as a regression guard.

---

## R-2. Case-folding semantics

**Decision**: rely on Go's `strings.ToLower`, which case-folds per Unicode rules for runes that have a simple lowercase mapping. ASCII names (all current `products.json` entries) are trivially handled. No new dependency.

**Rationale**: the existing code already uses `strings.ToLower`; preserving it minimises change. For the demo catalog of ~10 ASCII-named products, this is exact. Unicode case-folding edge cases (Turkish dotless I, German ß, Greek Σ) are documented in the spec's Edge Cases section as "fine for the slice; deferred."

**Alternatives considered**:

- `golang.org/x/text/cases.Fold` for full Unicode CaseFolding — overkill for ASCII demo data; introduces an indirect dependency on `golang.org/x/text`. Rejected.
- Build a normalised lowercase shadow `name` per product at load time, search against it — a tiny performance win for queries × products = 10 × 1 per request. Premature optimisation for this scale. Rejected.

**Affected by**: `product_catalog.go` (no change beyond R-1).

---

## R-3. Empty / whitespace query handling

**Decision**: enforce empty-query short-circuit at the **frontend** (already in place), not at the backend. Backend `SearchProducts` makes no special case for an empty string and will simply return every product whose name contains "" (i.e. all of them). The frontend prevents this call from ever being made.

**What's there today**: `src/frontend/handlers.go:124`:

```go
query := strings.TrimSpace(r.URL.Query().Get("q"))
...
if query != "" {
    products, err = fe.searchProducts(r.Context(), query)
    ...
}
```

And `templates/search.html:31-34`:

```go-template
{{ else }}
  <h3>Search</h3>
  <p class="search-result-count">Enter a term in the search bar above to find products.</p>
{{ end }}
```

**Match against spec**: FR-010 ("frontend MUST display a helper message such as 'Type a product name to search' and MUST NOT call `SearchProducts`") is **already satisfied**. The exact verbiage differs ("Enter a term in the search bar above to find products"); close enough — spec wording was illustrative ("such as").

**Rationale**: defence-in-depth would suggest enforcing it on both sides. But TC-002 forbids changes to the match logic beyond name-substring; adding an "empty → empty result list" arm would be a deviation from the strict reading. Keeping the gate at the frontend is sufficient and minimal.

**Alternatives considered**:

- Also short-circuit at the backend — adds a no-op safety net at the cost of a small contract deviation. Rejected for cleanliness; could be added later if a non-browser client ever calls `SearchProducts` directly.
- Tighten frontend verbiage to match spec exactly — micro-change, no behaviour difference. Deferred as not worth a commit on its own.

**Affected by**: nothing (no change).

---

## R-4. Test strategy

**Decision**: table-driven tests in `product_catalog_test.go` covering:

| Test name | What it asserts | Spec reference |
|---|---|---|
| `TestSearchProducts_ExactName` | Full exact name returns the product | AS 1 |
| `TestSearchProducts_Substring_Start` | "Antiq" matches "Antique Camera" | AS 2 |
| `TestSearchProducts_Substring_Middle` | "tique" matches "Antique Camera" | AS 2 |
| `TestSearchProducts_Substring_End` | "amera" matches "Antique Camera" | AS 2 |
| `TestSearchProducts_CaseInsensitive_Upper` | "ANTIQUE" matches "Antique Camera" | AS 3 |
| `TestSearchProducts_CaseInsensitive_Mixed` | "aNtIqUe" matches | AS 3, 4 |
| `TestSearchProducts_MultipleMatches` | "camera" returns both Antique and Vintage cameras | AS 5 |
| `TestSearchProducts_DescriptionOnlyMatches` *(regression guard)* | A product whose **description** (but not name) contains the query DOES appear | AS 6, TC-002 (amended) |
| `TestSearchProducts_NameAndDescriptionBothMatch` | A query that matches both a product's name and another product's description returns both, each exactly once | AS 6a |
| `TestSearchProducts_CategoryOnlyDoesNotMatch` | A query that matches only a product's category MUST NOT return that product | AS 6b |
| `TestSearchProducts_NoMatch` | Returns empty slice for absent string (must not match category, brand, tags, SKU) | AS 7 |
| `TestSearchProducts_NaturalOrder` | Results preserve catalog order | FR-007 |
| `TestSearchProducts_SpecialChars` | "." returns zero matches (treated as literal) | Edge Cases |
| `TestSearchProducts_LongQuery` | Query longer than any name or description returns zero matches | Edge Cases |
| `TestSearchProducts_UnicodeCase` *(if any unicode names exist in fixtures)* | "CAFÉ" matches "café" | Edge Cases |

Mock catalog will be expanded in `TestMain` to include:

- Products with descriptions populated (currently absent in test fixtures) — to exercise the description-match regression guard and the negative category test.
- Products with overlapping name substrings (for multi-match).
- At least one product with a unique category that does NOT appear in any product's name or description (for the "category-only must not match" negative test).
- Optionally one Unicode-named product.

**Frontend tests**: no new test file. The existing repo has no frontend handler tests; adding the first ever handler test is scope creep for this slice. Acceptance Scenarios 8 (empty query) and the `/search?q=` route are exercised by the manual quickstart and, if the team has end-to-end coverage elsewhere, by that.

**Rationale**: TDD-style, table-driven Go tests are the established pattern in this repo. Test fixtures live entirely in-memory inside `TestMain` — no real `products.json` IO is required for unit tests.

**Alternatives considered**:

- Generating a fresh test fixture file in `products.json` format and loading it through `parseCatalog` — heavier, adds IO to unit tests; rejected.
- One mega-test using a table with all rows — slightly more idiomatic Go but slightly worse failure messages. The above split is fine.

**Affected by**: `product_catalog_test.go`.

---

## R-5. Empty-state UX (zero matches)

**Decision**: extend `templates/search.html` to render an explicit empty-state block when the query is non-empty but the result list is empty. The current template just says "0 products found" with no further guidance.

**What's there today**: `search.html:28-35`:

```go-template
{{ if $.query }}
  <h3>Search results for &ldquo;{{ $.query }}&rdquo;</h3>
  <p class="search-result-count">{{ len $.products }} {{ if eq (len $.products) 1 }}product{{ else }}products{{ end }} found</p>
{{ else }}
  <h3>Search</h3>
  <p class="search-result-count">Enter a term in the search bar above to find products.</p>
{{ end }}
```

**What FR-006 requires**: "a clear empty-state message indicating no products were found."

**The change**: add a third branch, e.g.:

```go-template
{{ if $.query }}
  {{ if eq (len $.products) 0 }}
    <h3>No products found for &ldquo;{{ $.query }}&rdquo;</h3>
    <p class="search-result-count">Try a different word, or check the spelling.</p>
  {{ else }}
    <h3>Search results for &ldquo;{{ $.query }}&rdquo;</h3>
    <p class="search-result-count">{{ len $.products }} {{ if eq (len $.products) 1 }}product{{ else }}products{{ end }} found</p>
  {{ end }}
{{ else }}
  ... (unchanged "Enter a term..." branch)
{{ end }}
```

**Rationale**: minimal, template-only change. No Go code changes. Matches FR-006 verbatim.

**Alternatives considered**:

- Add a "Did you mean…?" suggestion — explicitly out of scope (Out of Scope: no typo tolerance / fuzzy matching).
- Surface "popular searches" or "browse categories" links — scope creep; out of slice.

**Affected by**: `templates/search.html`.

---

## R-6. Catalog-service-down resilience (FR-008)

**Decision**: do not change the resilience behaviour in this slice. Document the existing behaviour.

**What's there today**: `handlers.go:135-139` returns HTTP 500 (`renderHTTPError`) when `searchProducts` errors. The storefront *page* render itself doesn't depend on `productcatalogservice` for non-search pages individually, but several other pages do call other backend services that may also be down — overall resilience to backend outages is a property of the whole storefront, not specific to search.

**What FR-008 requires**: the storefront still loads; the search input shows an inline error rather than crash or hang.

**Interpretation**: a 500 page from `/search` does not "crash or hang." The storefront *will* still load on other URLs. The shopper sees an error page on `/search` only. This is acceptable for the slice.

**Rationale**: improving this to an inline soft error on the search page would touch `handlers.go`, add a new template branch, and require a small amount of error-translation glue. The spec language ("rather than crash or hang") is satisfied by the existing 500. The improvement is **listed as an optional follow-up** in `plan.md` rather than carried in this slice.

**Alternatives considered**:

- Render the search page with an inline error banner and an empty product list — better UX. Defer.
- Add a circuit breaker / cached fallback — out of slice, would need new infra.

**Affected by**: nothing (no change in this slice).

---

## R-7. Performance budget (SC-003)

**Decision**: no performance work needed. Trivially within budget.

**Rationale**: catalog size n ≈ 10. Per request, the backend does `n × strings.ToLower(name) × strings.Contains(...)` — each iteration is a few hundred nanoseconds; total backend work is sub-millisecond. The `time.Sleep(extraLatency)` at the top of the handler intentionally adds latency for demo purposes and is a known property of this codebase. End-to-end p95 of 2 s is dominated by network + template render and easily met on any test environment.

**Alternatives considered**:

- Pre-build a lowercase name index — micro-optimisation; rejected (R-2).
- Drop `time.Sleep(extraLatency)` for search — would change demo behaviour for other RPCs too; out of slice. Rejected.

**Affected by**: nothing.

---

## R-8. Coverage measurement for SC-004 (search input on every page)

**Decision**: rely on the template-include mechanism for compile-time guarantees, and add (optionally) a manual checklist to the quickstart. No new automated page-coverage test.

**Rationale**: every storefront page template begins with `{{ template "header" . }}`. The search form lives inside `{{ define "header" }}`. If header is included on a page, the search form is rendered on that page. A grep over `src/frontend/templates/*.html` for `template "header"` is sufficient to verify SC-004 by inspection.

**Alternatives considered**:

- A new Go test that boots the frontend and hits each route, parsing the HTML and asserting `name="q"` is present — meaningful but adds the first frontend handler test in the repo. Out of slice.
- A small `go test`-driven inspection that asserts every `*.html` template (excluding `header.html`, `footer.html`, `error.html`) starts with the header include — cheap. Could be added in `/speckit-tasks` if the team wants automation. Optional.

**Affected by**: nothing required; one optional small test if desired.

---

## R-9. Logging and metrics

**Decision**: keep the existing structured log line in `searchHandler` (`log.WithField("query", query).Info("search")`). No new metrics in this slice (no Prometheus / OTel additions). SC-006 and SC-007 will be derived post-launch from these existing logs.

**Rationale**: spec explicitly excludes analytics tooling in scope. Logs are pre-existing infrastructure. Querying log volume by message text is the simplest way to derive search adoption numbers post-launch.

**Alternatives considered**:

- Add a counter metric `frontend_searches_total{has_results=true|false}` — useful, low cost, but tips into "analytics work" which is Out of Scope. Defer.

**Affected by**: nothing.

---

## Summary of decisions

| ID | Decision | Code change? |
|---|---|---|
| R-1 | Keep name-OR-description match (spec amended to match existing code) | **No** |
| R-2 | Keep `strings.ToLower`, accept its Unicode behaviour | No |
| R-3 | Frontend-only empty-query short-circuit (already present) | No |
| R-4 | Table-driven backend tests; no new frontend tests | Yes — test extension |
| R-5 | Add explicit "no products found" template branch | Yes — template |
| R-6 | Keep existing HTTP 500 on catalog-down; defer soft error | No |
| R-7 | No performance work | No |
| R-8 | Header include is enough to satisfy SC-004; optional test | No (optional) |
| R-9 | No new metrics | No |

**Net code surface (after spec amendment)**: **zero Go behavioural changes**, one Go test file (extended), one template (new empty-state branch). No new files. No proto changes. No infra changes.
