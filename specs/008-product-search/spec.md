# Feature Specification: Product Search (thin slice)

**Feature Branch**: `008-product-search`

**Created**: 2026-06-02

**Status**: Draft

**Input**: User description: "Add a product search feature to Online Boutique. Frontend + lightweight backend slice: a search box that calls a new SearchProducts(query) RPC on productcatalogservice, returning matches by product name (case-insensitive substring)."

**Amendment (2026-06-02, post-plan reality check)**: the matching scope was widened from `name` only to `name` OR `description`, both as case-insensitive substring. This aligns the spec with the existing behaviour of `SearchProducts` on this branch and with the workshop's prior "restore description match" commit. All other constraints (no other fields, no fuzzy, no ranking, no new services, no new datastores, etc.) are unchanged.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Find a product by name (Priority: P1)

A shopper on Online Boutique knows roughly what a product is called — or remembers a fragment of its name — and wants to jump straight to it instead of walking through category pages. They type that fragment into a search box on the storefront, submit, and see the matching product (or products) listed with a link to each. They click through to the product page in a single step.

**Why this priority**: This is the entire slice. Without it, there is no search feature. It is also independently valuable on day one — even with no ranking, no typo tolerance, and no analytics, a shopper who knows part of a product's name can now find it in one step instead of clicking through category navigation. It is the minimum viable search.

**Independent Test**: Pick any product in the existing catalog. Type part of its exact name (any contiguous substring, any case) into the search box on the storefront, submit, and confirm the product appears in the result list with a working link to its product detail page. Completes the journey from "I know what I want" to "I'm on the product page" in two interactions (type + click).

**Acceptance Scenarios**:

1. **Given** a catalog containing a product named "Antique Camera", **When** the shopper types `Antique Camera` into the search box and submits, **Then** "Antique Camera" appears in the results list with a link to its product detail page.
2. **Given** the same product, **When** the shopper types `amera` (a substring of the name) and submits, **Then** "Antique Camera" appears in the results list.
3. **Given** the same product, **When** the shopper types `ANTIQUE` (different case from the stored name) and submits, **Then** "Antique Camera" appears in the results list.
4. **Given** the same product, **When** the shopper types `antique camera` (lowercase) and submits, **Then** "Antique Camera" appears in the results list.
5. **Given** a catalog containing both "Antique Camera" and "Vintage Camera", **When** the shopper types `camera` and submits, **Then** both products appear in the results list.
6. **Given** a catalog containing a product whose **description** (but not name) contains the word "lens", **When** the shopper types `lens` and submits, **Then** that product **does** appear in the results list (description matching is intentional — see Amendment).
6a. **Given** a catalog containing one product whose **name** contains "lens" and a different product whose **description** but not name contains "lens", **When** the shopper types `lens` and submits, **Then** both products appear in the results list.
6b. **Given** a catalog containing a product whose **category** is "cameras" but whose name and description do not contain "cameras", **When** the shopper types `cameras` and submits, **Then** that product does **not** appear (categories, tags, brand, SKU, etc. are still out of matching scope).
7. **Given** a catalog with no products whose name contains the typed text, **When** the shopper types `xyznonsense` and submits, **Then** an empty-state message is shown indicating no products were found.
8. **Given** the search box is visible, **When** the shopper clicks into it and presses Enter without typing (or types only whitespace), **Then** the system displays a helper message such as "Type a product name to search" and makes no call to `SearchProducts`.
9. **Given** any submitted query, **When** results are returned, **Then** they are displayed in the natural order returned by the catalog service (no client-side reordering, no ranking score).

### Edge Cases

- **Whitespace-only query** — treated identically to an empty query: helper message shown, no `SearchProducts` call made.
- **Leading/trailing whitespace** — trimmed before matching (the substring `camera ` and `camera` produce the same result set).
- **Unicode names** — products with non-ASCII characters in their name match case-insensitively per Unicode case-folding rules (e.g. `café` matches `CAFÉ`). If the catalog contains no such products, this is moot for the slice.
- **Very long query** — queries longer than the longest product name simply return zero results (no error).
- **Special regex characters in query** (`.`, `*`, `(`, etc.) — treated as literal characters, not pattern syntax. A query of `.` does not match every product.
- **Product becomes unavailable mid-session** — the catalog service is the source of truth; results reflect whatever the catalog returns at query time. No special handling.
- **Catalog service unavailable** — the storefront page still loads; the search input shows an inline error rather than crashing.

## Requirements *(mandatory)*

### Functional Requirements — observable behaviour

- **FR-001**: A search input MUST be visible to the shopper in the global storefront header on every storefront page (home, category listings, product detail, cart, checkout — every page rendered by the `frontend` service).
- **FR-002**: The search input MUST accept free-text input of at least 1 character.
- **FR-003**: When the shopper submits a query, the system MUST display every product whose **name OR description** contains the query text as a case-insensitive substring.
- **FR-004**: When the shopper submits a query, the system MUST NOT display any product whose name AND description both fail to contain the query text. (Category, tags, brand, SKU, and any other product field MUST NOT influence matching in this slice. Description matching is allowed — see TC-002 — but no other field beyond name and description.)
- **FR-005**: Each result MUST display the product name and a working link to that product's existing detail page.
- **FR-006**: When zero products match, the system MUST display a clear empty-state message indicating no products were found.
- **FR-007**: Results MUST be displayed in the natural order returned by the catalog service; the storefront MUST NOT reorder, rank, or score them.
- **FR-008**: If the catalog service is unreachable, the storefront page MUST still render and the search input MUST display an inline error rather than crash or hang.
- **FR-009**: The system MUST return all products that match the query; no cap or pagination is applied. (Safe in this slice because the catalog is ~10 products; scaling is explicitly deferred.)
- **FR-010**: When the submitted query (after trimming leading/trailing whitespace) is empty, the frontend MUST display a helper message such as "Type a product name to search" and MUST NOT call `SearchProducts`. No request reaches `productcatalogservice` for an empty query.

### Technical Constraints — intentional implementation directives

These items are normally out of place in a spec, but the slice is *defined* by them and downstream phases (`/speckit-plan`, `/speckit-tasks`, `/speckit-implement`) must honour them as hard constraints. They are non-negotiable.

**Match logic & RPC shape**

- **TC-001**: The frontend MUST call a new gRPC method `SearchProducts(query)` on the existing `productcatalogservice`. No other service may serve search.
- **TC-002**: The matching logic in `SearchProducts` MUST be a case-insensitive substring test against the product's `name` field **OR** its `description` field (the product matches if EITHER field, after lowercasing, contains the lowercased query as a substring). No other field may participate. No tokenisation, stemming, fuzzy matching, scoring, or alternative match strategies are permitted in this slice. Each matching product appears in results at most once, regardless of whether the query matched its name, its description, or both.

**Data source & runtime shape**

- **TC-003**: Search MUST operate over the existing in-memory product catalogue loaded from `productcatalogservice/products.json`. Filtering MUST happen in memory inside `productcatalogservice`. No new datastore, search index, cache layer, or out-of-process data source may be introduced (no Elasticsearch, Solr, OpenSearch, vector DB, Redis-as-index, SQLite, etc.).
- **TC-004**: All backend code MUST be Go (the existing language of `productcatalogservice`). All frontend changes MUST be in Go (the existing language of the `frontend` service). Any extension of `productcatalogservice` MUST follow the existing protobuf / gRPC patterns already in the repository (`protos/demo.proto`, regenerated stubs, established service-handler conventions).

**Service topology & deployment**

- **TC-005**: No new microservices. The slice extends `productcatalogservice` and `frontend` only.
- **TC-006**: No new infrastructure. No new Helm charts, Kubernetes manifests, Kustomize overlays, Terraform resources, Istio manifests, or environment variables. The change MUST be deployable by the existing CI pipeline as-is, with zero pipeline modifications.
- **TC-007**: Work stays inside this repository and this branch. No changes to build configuration (`cloudbuild.yaml`, `skaffold.yaml`, GitHub Actions workflows, Dockerfiles beyond what is strictly required to compile the new Go code into the existing images).
- **TC-008**: This feature branch (`008-product-search`) must merge cleanly into `attendee/matthew-buckland` for CI to deploy it. The CI pipeline deploys whatever lands on that attendee branch; no additional deploy step or environment is being introduced.

### Key Entities

- **Product** — the existing product entity in `productcatalogservice`. **No schema changes** are introduced by this slice. Search uses the existing `name` field only.
- **Search query** — a transient free-text input provided by the shopper. Not persisted in this slice.
- **Search result list** — a transient ordered list of product references returned by `SearchProducts(query)`. Not persisted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (correctness, exhaustive)**: For any test product in the catalog and any non-empty substring of that product's **name or description**, querying the substring returns that product in the result list. Verified by an automated test suite covering every product in the catalog with at least three substring variants each (start, middle, end) per matchable field, and three case variants (lower, upper, mixed).
- **SC-002 (correctness, no false positives)**: For any query whose text does not appear in any product's name **and** does not appear in any product's description (both after case-folding), the result list is empty. Verified by automated tests against the catalog using known-absent strings.
- **SC-003 (speed, user-facing)**: From the moment the shopper submits a query, results (or the empty-state message) appear on screen within 2 seconds at the 95th percentile under normal storefront load.
- **SC-004 (reach)**: The search input is present in the rendered HTML of every storefront page (home, category, product detail, cart, checkout). Verified by an automated page-coverage test that requests each page and asserts the search input element is present.
- **SC-005 (resilience)**: When the catalog service is artificially made unavailable in a test environment, the storefront page still loads in full and the search input renders an error state. No 5xx page is served to the shopper.
- **SC-006 (adoption, post-launch)**: Within 30 days of release, ≥ 20% of unique shopper sessions on the storefront submit at least one search query. (Baseline measurement begins on the release day; this target is the indicator that the feature is reaching users.)
- **SC-007 (effectiveness, post-launch)**: ≥ 60% of submitted searches that return at least one result are followed by a click on a result within 10 seconds. (Reported via existing storefront request logs; no new analytics infrastructure is in scope for this slice — see Out of Scope below.)

## Assumptions

- The product catalog (`productcatalogservice/products.json`) is the source of truth for product names; no separate index is introduced.
- The existing storefront framework (Go templates), styling system, and page layout are reused for the search input and results display.
- Shoppers may be signed in or anonymous; behaviour is identical for both.
- The catalog is small enough today (~10 products in `products.json`) that a linear in-memory scan in `productcatalogservice` is acceptable for this slice. Scaling concerns are deferred.
- Product names are in a single language (matching the existing storefront locale). Multi-locale search is not in scope.
- The existing protobuf definition (`protos/demo.proto`) and gRPC service-handler conventions in `productcatalogservice` are sufficient to add `SearchProducts`; no service-mesh, auth, or networking changes are required.
- This feature branch (`008-product-search`) will be merged back to `attendee/matthew-buckland`; CI deploys whatever lands there. No separate environment, no manual deploy step.
- Post-launch metrics SC-006 and SC-007 can be derived from existing storefront request logs without adding new analytics pipelines.

## Out of Scope — explicit non-goals

Listed verbatim from the slice's defining constraints, plus consequential exclusions:

- **External search infrastructure** — no Elasticsearch, OpenSearch, Solr, Algolia, Meilisearch, Typesense, vector databases, or any third-party search service.
- **New microservices** — search MUST live inside the existing `productcatalogservice`. No new deployable component.
- **New datastores or indexes** — the existing in-memory `products.json` is the *only* data source. No new tables, no new caches, no separate search index, no embedding store.
- **UI framework swap** — the storefront's existing Go templating remains; no React/Vue/MUI or any other JS-framework introduction in this slice.
- **Schema changes** — no new fields on `Product`, no new tables, no new indexes, no migration.
- **New infrastructure config** — no new Helm charts, Kubernetes manifests, Kustomize overlays, Terraform resources, Istio manifests, or environment variables.
- **Build / CI / deployment pipeline changes** — no edits to `cloudbuild.yaml`, `skaffold.yaml`, GitHub Actions workflows, or any deploy tooling. CI deploys whatever lands on `attendee/matthew-buckland` as-is.
- **Cross-repo work** — all changes live in this repository. No sibling repos, no shared-library extractions.
- **Analytics tracking** — no Segment, Snowplow, GA4 event wiring, or any new analytics SDK. SC-006/SC-007 are measured from existing logs only.
- **Typo tolerance / fuzzy matching** — exact case-insensitive substring only. "Acne Runing" does NOT find "Acme Running Shoe" in this slice.
- **Ranking beyond natural order** — no relevance score, no popularity boost, no personalisation, no recency, no learning-to-rank.
- **Matching fields other than name or description** — category, brand, tags, SKU, attributes, reviews, and seller name MUST NOT influence results. (Description matching IS in scope per TC-002 / FR-003 as amended.)
- **Live results as the shopper types** — submit-based; no debounced as-you-type queries in this slice.
- **Autocomplete / suggestions** — no dropdown of suggested completions while typing.
- **Pagination, sorting controls, filters** — none in this slice. Results are a single list in catalog order.
- **Personalisation** — signed-in shoppers see the same results as anonymous shoppers.
- **Voice or image search**.
- **Cross-catalog search** — only Online Boutique's own catalog.
- **Back-in-stock notifications** — out of stock products appear normally in this slice (no badge, no subscribe action). A separate feature.
- **Admin / merchandiser-facing search tooling**.

## Resolved Clarifications

All three clarifications raised during specification have been resolved. No `[NEEDS CLARIFICATION]` markers remain in the spec.

- ~~**Q1 (scope of placement)**~~ — **Resolved**: global storefront header on every page. See FR-001 and SC-004.
- ~~**Q2 (empty query behaviour)**~~ — **Resolved**: show a helper message ("Type a product name to search"); no `SearchProducts` call is made. See FR-010 and Acceptance Scenario 8.
- ~~**Q3 (result cap)**~~ — **Resolved**: return all matches, no cap or pagination. See FR-009.

The spec is ready for `/speckit-plan` without an intermediate `/speckit-clarify` pass.
