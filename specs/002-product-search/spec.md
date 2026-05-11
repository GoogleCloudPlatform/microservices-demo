# Feature Specification: Product Search by Name

**Feature Branch**: `002-product-search`
**Created**: 2026-05-11
**Status**: Draft
**Input**: User description: "Frontend + lightweight backend. A search box that calls a new SearchProducts(query) RPC on productcatalogservice returning matches by product name (case-insensitive substring)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find a product by typing part of its name (Priority: P1)

A shopper visits the storefront with a specific product in mind (e.g. "watch", "sunglasses", "candle"). Instead of scrolling the catalog or guessing categories, they type a fragment of the product name into a search box on the storefront and immediately see the matching products laid out the same way as the regular catalog listing. From a result they can click through into the existing product detail page and continue the normal purchase flow.

**Why this priority**: This is the entire feature. Without it the shopper has no way to query the catalog by name — every other story is an embellishment on this core interaction.

**Independent Test**: Type "watch" into the search box on the storefront and confirm that the product named "Watch" appears in the results. Click the result and verify the existing product detail page loads. No other story needs to ship for this to be valuable on its own.

**Acceptance Scenarios**:

1. **Given** a shopper is on any storefront page, **When** they type `watch` into the search box and submit, **Then** the product named "Watch" appears in the results.
2. **Given** a shopper is searching, **When** they type `WATCH` (uppercase) or `Watch` (mixed case), **Then** the same product named "Watch" appears — case has no effect on matching.
3. **Given** the shopper types a substring that appears inside a longer name (e.g. `lass` to match "Sunglasses"), **When** they submit the search, **Then** every product whose name contains that substring is returned.
4. **Given** a shopper has submitted a search, **When** they click a result, **Then** they land on the existing product detail page for that product and can add it to the cart through the existing flow.

---

### User Story 2 - Receive clear feedback when nothing matches (Priority: P2)

When a shopper searches for something the catalog doesn't carry (e.g. "laptop"), they should see an unambiguous "no results" state rather than a blank screen or an apparent error, so they know the search ran and they can try a different term.

**Why this priority**: The feature still delivers value without this — the page just looks empty — but the missing affordance erodes trust and makes shoppers think the site is broken. Cheap to add once Story 1 is in place.

**Independent Test**: Search for a term that has no matches in the catalog (e.g. `laptop`) and confirm a "no results" message is shown along with the original search box so the shopper can retry.

**Acceptance Scenarios**:

1. **Given** the shopper submits a query with no matches, **When** the page renders, **Then** a "no results" message is displayed in place of the product grid and the search box remains visible and pre-filled with the query so it can be edited.
2. **Given** an empty or whitespace-only query is submitted, **When** the page renders, **Then** the storefront does not show a "no results" message — it returns the shopper to the regular catalog view (idle state).

---

### Edge Cases

- **Empty / whitespace-only query**: The system MUST NOT treat this as "match nothing"; it returns the shopper to the regular catalog view.
- **Leading and trailing whitespace**: Trimmed before matching, so `"  watch  "` behaves identically to `"watch"`.
- **Mixed case input**: Matching is fully case-insensitive (`"WATCH"`, `"Watch"`, `"watch"` are equivalent).
- **Substring inside name**: A query that appears anywhere in the name counts as a match (`"lass"` matches "Sunglasses").
- **Special characters in query** (e.g. apostrophes, punctuation): Matched literally; no regex semantics are exposed to the shopper.
- **Unicode characters in query**: Compared in a Unicode-safe, case-insensitive manner against the product name.
- **Very long query**: A query longer than any product name simply returns no results; the system does not error.
- **Multiple matches**: Returned in the same order the catalog already uses; ranking and relevance scoring are out of scope.
- **Catalog changes mid-search**: Each search reflects the catalog as currently loaded by the existing product catalog service; no staleness contract beyond what that service already provides.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The storefront MUST expose a search box that accepts a free-text query and submits it to a single, dedicated search action on the product catalog.
- **FR-002**: The product catalog MUST expose a single search operation that takes a query string and returns the list of products whose **name** contains the query as a case-insensitive substring.
- **FR-003**: Matching MUST be case-insensitive and MUST match substrings anywhere within the product name (not just prefixes or whole words).
- **FR-004**: Matching MUST consider only the product **name** field. Description, category, and other product fields are out of scope for matching in this version.
- **FR-005**: Leading and trailing whitespace in the query MUST be ignored.
- **FR-006**: An empty or whitespace-only query MUST NOT trigger a search and MUST NOT show a "no results" state; the storefront returns the shopper to the regular catalog view.
- **FR-007**: When at least one product matches, the storefront MUST display the matching products using the same visual layout used for the existing catalog/category listing pages so that the click-through and add-to-cart flows remain unchanged.
- **FR-008**: When no products match a non-empty query, the storefront MUST display a clear "no results" message and keep the search box visible and pre-filled with the submitted query so the shopper can refine it.
- **FR-009**: The search box MUST be reachable from every storefront page (e.g. via the shared header) so the shopper does not have to navigate back to a particular page to search.
- **FR-010**: Selecting a product from the search results MUST take the shopper to the existing product detail page for that product, with no change to the existing detail / add-to-cart / checkout flows.
- **FR-011**: The search operation MUST be read-only and MUST NOT modify the catalog, the cart, or any other system state.
- **FR-012**: The product catalog MUST source its data from the catalogue it already loads at startup; the search operation MUST NOT introduce a new data store, index, or external dependency.

### Key Entities

- **Product**: The existing catalog item the storefront already knows how to display. Only the `name` attribute participates in matching for this feature; all other attributes (id, description, picture, price, categories) are passed through unchanged so the existing UI can render them.
- **Search Query**: A free-text string supplied by the shopper. After trimming and case-normalization it is compared as a substring against each product's name.
- **Search Result**: The ordered list of products whose name matches the query. Order follows the catalog's existing order; no ranking or scoring is introduced.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A shopper can find a known product by name in under **5 seconds** from the moment they decide to search (open search box, type a fragment, see the matching product).
- **SC-002**: For the current catalog size, search results render in under **500 ms** end-to-end (from the moment the shopper submits the query to the moment the results grid is visible) on a typical broadband connection.
- **SC-003**: **100 %** of products in the catalog are discoverable by typing any substring (length ≥ 2) of their name — there are no "hidden" products that the search cannot surface.
- **SC-004**: For queries with no matches, **100 %** of shoppers see an unambiguous "no results" message rather than a blank page or an apparent error.
- **SC-005**: The click-through rate from search results into product detail pages is at parity (within ±10 %) with the click-through rate from category listings, indicating the search results page is no harder to use than the existing catalog.

## Assumptions

- The feature is delivered by extending the storefront and the product catalog service that already exist in this repository. No new services are introduced.
- The product catalog service continues to load its catalogue from its existing in-memory source at startup; no new datastore (search engine, vector DB, cache, etc.) is introduced. In-memory filtering is acceptable at the current catalog size.
- The new search operation is exposed using the same inter-service-communication pattern the product catalog service already uses for its other operations, so the storefront can call it the same way it calls existing operations.
- Search scope is intentionally limited to the product **name** for this version. Searching by description, category, or fuzzy/typo-tolerant matching is explicitly out of scope and would be a follow-up feature.
- Result ordering follows the catalog's existing order. Relevance ranking, popularity ranking, and personalization are out of scope.
- Pagination is not required for this version — the catalog is small enough that all matching products fit comfortably on one page.
- No new infrastructure configuration is introduced: no new Helm charts, Kubernetes manifests, environment variables, secrets, or pipeline changes. The feature ships through whatever the existing branch's CI already deploys.
- Work is scoped to the current feature branch and this repository. The build pipeline and shared infrastructure are not modified.
- Existing observability (logs, traces, metrics) for the product catalog service is sufficient; no new dashboards or alerts are introduced as part of this feature.
