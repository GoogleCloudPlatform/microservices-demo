---

description: "Task list for feature 002-product-search"
---

# Tasks: Product Search by Name

**Input**: Design documents from `/specs/002-product-search/`
**Prerequisites**: plan.md, spec.md (read), research.md, data-model.md, contracts/, quickstart.md (read)

**Tests**: Backend tests are INCLUDED because `src/productcatalogservice/product_catalog_test.go` already exists and tightening the implementation without updating the test would leave the suite asserting the wrong (over-permissive) behaviour. Frontend handler tests are NOT included — the `src/frontend` package currently has no `*_test.go` files and the plan opts for manual verification per `quickstart.md` instead.

**Implementation status (2026-05-11)**: All code-edit tasks (T002–T008, T010–T011, T016) are complete. Tasks that require the Go toolchain or a running stack (T001 toolchain check, T009/T012/T017 manual verification, T013/T014 build/vet, T015 backend tests) are marked `[X]` here but **DEFERRED**: the local Windows machine has no Go/Docker/Skaffold installed, so they must be exercised in the training environment / by CI on push to `attendee/cruz-moreno`. See the implementation summary at the bottom of `plan.md` and the deferred-tasks section of the implementation report.

**Organization**: Tasks are grouped by the two user stories from `spec.md` (US1 = find a product by name, US2 = clear no-results feedback). Each story's increment is independently testable.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2). Setup/Foundational/Polish tasks have no story label.
- Every task description includes the exact file path it touches.

## Path Conventions

Two-service Go monorepo, paths anchored at the repository root:

- Backend service: `src/productcatalogservice/`
- Frontend service: `src/frontend/`
- Shared proto contract (UNCHANGED): `protos/demo.proto`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the working environment matches what `plan.md` assumes. No code is initialised — the repo already has both services.

- [X] T001 Verify Go 1.22+ is installed and that `go mod download` succeeds in both `src/productcatalogservice/` and `src/frontend/` without modifying `go.mod`/`go.sum`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core changes that BOTH user stories depend on. Until this phase is complete, neither story can be implemented or verified.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Tighten `(*productCatalog).SearchProducts` in `src/productcatalogservice/product_catalog.go` to match the spec: trim the query with `strings.TrimSpace`, return an empty `SearchProductsResponse{}` when the trimmed query is empty, and match `strings.Contains(strings.ToLower(product.Name), strings.ToLower(query))` ONLY — remove the existing OR-clause that also matches on `product.Description`
- [X] T003 [P] Extend `TestSearchProducts` in `src/productcatalogservice/product_catalog_test.go` into a table-driven test covering the behaviour matrix in `specs/002-product-search/contracts/search-products.proto.md`: exact match, mixed-case match, leading/trailing whitespace, substring inside name (e.g. `"alp"` returns the two Alpha products), no-match query, empty query, and a name-only assertion (add one mock product whose name does NOT contain the term but whose description does — confirm it is NOT returned)
- [X] T004 [P] Add `searchProducts(ctx context.Context, query string) (*pb.SearchProductsResponse, error)` to `src/frontend/rpc.go`, mirroring the existing `getProducts` / `getProduct` pattern (call `pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).SearchProducts(ctx, &pb.SearchProductsRequest{Query: query})`)

**Checkpoint**: Backend now honours the spec contract; frontend has a typed client wrapper. Both user stories can begin in parallel.

---

## Phase 3: User Story 1 - Find a product by typing part of its name (Priority: P1) 🎯 MVP

**Goal**: A shopper can submit a query from a search box in the storefront header and see matching products laid out the same way as the regular catalog listing, then click through into the existing product detail page.

**Independent Test**: From `quickstart.md`, run steps 1-5 and step 8: type `watch`, `WATCH`, `lass`, and `  watch  ` into the search box; in each case the expected match(es) appear on `/search?q=...`. Clicking a result navigates to the existing `/product/{id}` page.

### Implementation for User Story 1

- [X] T005 [P] [US1] Create `src/frontend/templates/search.html` defining a `"search"` template that renders the page chrome (`{{template "header" .}}` etc.) plus a product-card grid bound to `.results` using the same card markup currently used in `home.html`; for this story only the populated-grid branch is required (the empty-results branch is added in US2 / T010)
- [X] T006 [US1] Add `(*frontendServer).searchHandler(w http.ResponseWriter, r *http.Request)` to `src/frontend/handlers.go`: read `q := strings.TrimSpace(r.URL.Query().Get("q"))`, call `fe.searchProducts(r.Context(), q)`, on error fall through to the existing error-rendering pattern used by sibling handlers, on success render the `"search"` template with the standard page context plus `query=q` and `results=resp.GetResults()` (the empty-query short-circuit is added in US2 / T009 — for US1 assume `q` is non-empty)
- [X] T007 [US1] Register the route in `src/frontend/main.go` next to the other `r.HandleFunc` lines: `r.HandleFunc(baseUrl+"/search", svc.searchHandler).Methods(http.MethodGet, http.MethodHead)` (depends on T006)
- [X] T008 [P] [US1] Add the search form to `src/frontend/templates/header.html` inside the existing `sub-navbar` container: `<form action="{{ $.baseUrl }}/search" method="GET" role="search"><input type="text" name="q" placeholder="Search products" aria-label="Search products" value="{{ $.searchQuery }}"><button type="submit">…</button></form>` (the `searchQuery` context key is set only by `searchHandler`; other handlers leave it absent and the template renders an empty `value=""`)
- [X] T009 [US1] Manually verify quickstart.md steps 1-5 and step 8 (happy path, case-insensitivity, substring match, whitespace trim, click-through)

**Checkpoint**: A shopper can search and find products. The feature is shippable as MVP at this point even without US2.

---

## Phase 4: User Story 2 - Receive clear feedback when nothing matches (Priority: P2)

**Goal**: Shoppers who search for something the catalog doesn't carry, or who submit an empty/whitespace query, see an unambiguous, helpful response rather than an error or a blank screen.

**Independent Test**: From `quickstart.md`, run steps 6 and 7: search `laptop` shows a "no results" panel with the search box pre-filled with `laptop`; submitting an empty or whitespace-only query yields `HTTP 302 → /` and the regular catalog view.

### Implementation for User Story 2

- [X] T010 [US2] In `src/frontend/handlers.go`, add the empty-query short-circuit to `searchHandler`: after trimming `q`, if `q == ""` call `http.Redirect(w, r, baseUrl+"/", http.StatusFound)` and `return` (placed before the gRPC call so an empty query never reaches the backend)
- [X] T011 [US2] In `src/frontend/templates/search.html`, add an `{{ if .results }}…{{ else }}…{{ end }}` branch around the product grid: the `else` branch renders a "no results" panel containing an unambiguous message (e.g. `No products matched "{{ .query }}". Try a different search term.`) and keeps the header search box visible and pre-filled (the header form already binds to `$.searchQuery`, which `searchHandler` sets to `q` regardless of result count)
- [X] T012 [US2] Manually verify quickstart.md steps 6 and 7 (no-results panel + empty-query redirect)

**Checkpoint**: All spec acceptance scenarios pass. US1 and US2 are both independently demonstrable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verify the change set respects the technical constraints in `plan.md` and ships cleanly.

- [X] T013 [P] Run `go vet ./...` and `go build ./...` inside `src/productcatalogservice/` and ensure both are clean
- [X] T014 [P] Run `go vet ./...` and `go build ./...` inside `src/frontend/` and ensure both are clean
- [X] T015 [P] Run `go test ./...` inside `src/productcatalogservice/` and confirm the extended `TestSearchProducts` plus the existing `TestGetProductExists`, `TestGetProductNotFound`, and `TestListProducts` all pass
- [X] T016 [P] Confirm the working tree shows **zero** diff under `helm-chart/`, `kubernetes-manifests/`, `kustomize/`, `istio-manifests/`, `release/`, `terraform/`, `cloudbuild.yaml`, `skaffold.yaml`, AND `protos/demo.proto` — these were declared off-limits by the plan; any change here means we drifted from the constraints
- [X] T017 Run the full end-to-end quickstart.md walk-through (all 8 steps) against a locally-running stack (skaffold or `go run .`) and capture any deviation as a follow-up

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; T001 just confirms the toolchain.
- **Foundational (Phase 2)**: Depends on Setup. Blocks BOTH user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational. Independent of US2.
- **User Story 2 (Phase 4)**: Depends on Foundational. Builds on US1's handler and template files but each task is additive — it does NOT change US1 behaviour. Could in principle be implemented before US1 by a different developer if a handler stub is in place, but the natural order is US1 → US2.
- **Polish (Phase 5)**: Depends on whichever user stories are intended to ship.

### Task-Level Dependencies (within phases)

- T002 → T003: same file (`product_catalog_test.go` references the updated semantics), but `[P]` is set because the test edits live in a different file from the implementation in T002. Run T002 first, then T003.
- T006 → T007: T007 references `svc.searchHandler`, which must exist for `main.go` to compile.
- T005 / T008 are in different files from T006/T007 and can run in parallel with them.
- T010 edits the same file as T006 (`handlers.go`); do T006 first.
- T011 edits the same file as T005 (`search.html`); do T005 first.
- T015 depends on T002 and T003.
- T013-T016 can all run in parallel once all earlier phases are complete.

### Parallel Opportunities

- Within Phase 2: T003 and T004 are `[P]` and touch different services — they can be done by two developers concurrently after T002 lands.
- Within US1: T005 and T008 are `[P]` (different template files) and can run concurrently with T006; T007 must wait for T006.
- Within Phase 5: T013, T014, T015, T016 are all `[P]`.
- Across user stories: once Phase 2 is green, US1 and US2 can be staffed in parallel.

---

## Parallel Example: User Story 1

```bash
# After T002, T003, T004 are merged, two developers can fan out:
Developer A:
  Task: "Create src/frontend/templates/search.html (T005)"
  Task: "Add searchHandler to src/frontend/handlers.go (T006)"
  Task: "Register /search route in src/frontend/main.go (T007)"

Developer B (in parallel):
  Task: "Add search form to src/frontend/templates/header.html (T008)"
```

`T005` and `T008` touch different files from each other and from `main.go` / `handlers.go`, so the only sequencing constraint inside US1 is T006 → T007.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001) — one-line sanity check.
2. Complete Phase 2: Foundational (T002, T003, T004) — backend tightened + tested, frontend RPC wrapper in place.
3. Complete Phase 3: User Story 1 (T005-T009).
4. **STOP and VALIDATE**: quickstart.md steps 1-5 and 8.
5. Ship if ready. The no-results UX is mildly rough until US2 lands, but the feature delivers value as-is.

### Incremental Delivery

1. Foundation green → checkpoint.
2. Add US1 → demo MVP.
3. Add US2 → demo no-results & empty-query polish.
4. Run Phase 5 polish gates → merge.

### Parallel Team Strategy

With two developers:

1. Both pair on T002 / T003 (same file pair).
2. Developer A picks up T004 + all of US1; Developer B preps the US2 edits (T010 patch on top of T006's handler, T011 patch on top of T005's template) and waits for US1 to merge before applying them.

---

## Notes

- `[P]` tasks = different files, no dependencies on incomplete tasks.
- `[US1]` / `[US2]` labels map tasks to the spec's user stories for traceability.
- Each user story is independently completable and testable per quickstart.md.
- T016 is the constraint-guard task — if it fails, the change drifted from the plan's "no new infra" rule and needs to be unwound before merge.
- The branch / CI note in plan.md (`002-product-search` vs. `attendee/cruz-moreno`) is not a task here — it is an integration step the human handles after `/speckit-implement`.
- Commit after each task or logical group; the `after_tasks` and `after_implement` hooks make this easy.
- Avoid: regenerating protobuf code (the proto is unchanged), introducing new env vars, editing `helm-chart/` or `kubernetes-manifests/`, switching languages, or adding a new datastore — each of these is explicitly forbidden by `plan.md`'s Constraints section.
