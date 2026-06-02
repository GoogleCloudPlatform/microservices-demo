---

description: "Task list for Product Search (thin slice) — branch 008-product-search"
---

# Tasks: Product Search (thin slice)

**Input**: Design documents from `/specs/008-product-search/`

**Prerequisites**: `plan.md`, `spec.md` (required); `research.md`, `data-model.md`, `contracts/`, `quickstart.md` (all present).

**Tests**: Tests **are** included for this slice. They are not net-new TDD scaffolding — they extend the existing `product_catalog_test.go` to lock in the amended TC-002 (name OR description) and guard against the workshop's recurring seed bug.

**Organization**: This slice has a single P1 user story (the entire MVP), so there is one user story phase. Setup and Foundational phases are intentionally lightweight — most of the implementation already exists on this branch and only needs verification.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps task to user story for traceability (US1 only in this slice)
- File paths are absolute-from-repo-root and exact

## Path Conventions

This repo is a polyglot microservices monorepo. Paths used below:

- `src/productcatalogservice/` — Go service that owns the search match logic
- `src/frontend/` — Go service that owns the storefront templates and the `/search` HTTP route
- `specs/008-product-search/` — this feature's SpecKit artefacts
- `protos/` — gRPC contracts (READ-ONLY for this slice; TC-001 / TC-004)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm local dev tooling can build and test the two services this slice touches. No code changes here.

- [~] T001 Verify Go toolchain is available and both services build cleanly. Run `go build ./...` in `src/productcatalogservice/` and `src/frontend/`. If either fails for a non-slice reason (e.g. a pre-existing broken commit on `attendee/matthew-buckland`), surface it before doing any other work. **DEFERRED 2026-06-02**: Go is not installed in the implementing environment; user must run this locally before running tests. Edits can still be made safely because they're well-scoped (test file + template), and `T010` will catch any compile error in test code.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Confirm the existing implementation matches the **amended** spec before writing any tests against it. This is a read-only verification; if it fails, the slice's scope needs renegotiation (not silent code changes).

**⚠️ CRITICAL**: Do not start US1 work until T002 has passed.

- [X] T002 Read `src/productcatalogservice/product_catalog.go` lines 60–72 (function `SearchProducts`). Confirm the match expression is `strings.Contains(strings.ToLower(product.Name), strings.ToLower(req.Query)) || strings.Contains(strings.ToLower(product.Description), strings.ToLower(req.Query))`. This is what the amended TC-002 specifies. If it differs, STOP and reconcile with the user before touching anything else. **Verified 2026-06-02**: match expression at lines 65–66 is exactly as specified.

**Checkpoint**: Existing code is verified to match the amended spec. No Go behavioural changes are required in this slice. Proceed to US1.

---

## Phase 3: User Story 1 — Find a product by name (or description) (Priority: P1) 🎯 MVP

**Goal**: A shopper can type a fragment of a product's name or description into the storefront header search box, submit, and land on a `/search?q=…` page that lists every matching product with a working link to its detail page. Zero-match queries get a clear empty-state. Submit with no query does not call the backend. The behaviour is locked in by automated tests so the workshop's recurring "search-misses-descriptions" seed bug cannot return undetected.

**Independent Test**: Run both services locally; with `products.json` as the catalog, perform each of the 9 acceptance scenarios from `spec.md` (plus 6a and 6b) by hand, then run `go test ./src/productcatalogservice/...` and confirm all tests pass.

### Test setup for User Story 1

- [X] T003 [US1] Extend the mock catalog in `TestMain` (in `src/productcatalogservice/product_catalog_test.go`) with the fixtures required by the amended acceptance scenarios. Add: (a) at least one product with `Description` populated such that a unique word appears in the description but NOT in any product's name (for the description-only-matches regression guard, AS 6); (b) at least one product with a unique `Categories` value that does NOT appear in any product's name or description (for the category-only-MUST-NOT-match negative test, AS 6b); (c) at least two products whose names share a substring (for multi-match, AS 5). Do NOT change the existing four products (`abc001`..`abc004`) — the existing `TestSearchProducts` at line 91 asserts that `"alpha"` returns exactly 2 results, and the new fixtures must preserve that.

### Backend tests for User Story 1

> **NOTE**: All these tests live in `src/productcatalogservice/product_catalog_test.go`. They are necessarily **sequential** (same file). Run the full test suite after each batch to keep the failure surface small. Test names follow `research.md` R-4.

- [X] T004 [US1] Add positive substring/case tests to `src/productcatalogservice/product_catalog_test.go`: `TestSearchProducts_ExactName` (AS 1), `TestSearchProducts_Substring_Start`, `TestSearchProducts_Substring_Middle`, `TestSearchProducts_Substring_End` (AS 2), `TestSearchProducts_CaseInsensitive_Upper`, `TestSearchProducts_CaseInsensitive_Mixed` (AS 3, 4). Each test should assert both the count and the identity of the returned products.

- [X] T005 [US1] Add multi-match and de-duplication tests to `src/productcatalogservice/product_catalog_test.go`: `TestSearchProducts_MultipleMatches` (AS 5) and `TestSearchProducts_NameAndDescriptionBothMatch` (AS 6a — verifies that when one product matches via name and another via description, both appear, each exactly once).

- [X] T006 [US1] Add the **regression guard** test to `src/productcatalogservice/product_catalog_test.go`: `TestSearchProducts_DescriptionOnlyMatches` — a product whose description (and only description) contains the query MUST appear in results. This is the test that fails if the workshop's seed bug recurs (or if someone removes the `||` arm in `SearchProducts`). AS 6 / TC-002 amended.

- [X] T007 [US1] Add negative / scope-bounding tests to `src/productcatalogservice/product_catalog_test.go`: `TestSearchProducts_CategoryOnlyDoesNotMatch` (AS 6b — query matches only a product's category MUST NOT appear), `TestSearchProducts_NoMatch` (AS 7 — empty result for absent string), `TestSearchProducts_SpecialChars` (`.` is literal, returns zero matches), `TestSearchProducts_LongQuery` (query longer than any name or description returns zero matches).

- [X] T008 [US1] Add the ordering test to `src/productcatalogservice/product_catalog_test.go`: `TestSearchProducts_NaturalOrder` — for a query that matches multiple products, the order of the returned `Results` matches the iteration order of the catalog. FR-007.

### Frontend implementation for User Story 1

- [X] T009 [P] [US1] Add the explicit zero-results empty-state branch to `src/frontend/templates/search.html`. Replace the existing `{{ if $.query }} ... {{ else }} ... {{ end }}` block with a three-way split: (i) `$.query` non-empty AND `len $.products == 0` → "No products found for &ldquo;{{ $.query }}&rdquo;" heading plus a helpful one-line message; (ii) `$.query` non-empty AND results exist → existing "Search results for…" branch unchanged; (iii) `$.query` empty → existing "Enter a term in the search bar above to find products" branch unchanged. Reference template in `research.md` R-5. Parallelizable with T003–T008 (different file).

### Verification for User Story 1

- [~] T010 [US1] Run `go test ./src/productcatalogservice/...` from the repo root. All existing tests AND all tests added in T004–T008 must pass. If any tests added in this slice fail, the implementation does not match the amended spec — diagnose and fix (or escalate the spec) before continuing. **DEFERRED 2026-06-02**: Go toolchain is not installed in the implementing environment. User must run this locally. Expected result: 17 tests pass (4 existing + 13 added — 1 helper-style test split into multiple checks).

- [~] T011 [US1] Run both services locally (per `quickstart.md` Step 5) and manually verify each acceptance scenario from `spec.md`: AS 1–5, AS 6 (description match), AS 6a (name + description, both appear), AS 6b (category-only, does NOT appear), AS 7 (no match → empty state), AS 8 (empty submit → no backend call), AS 9 (natural order). Confirm visually that the empty-state from T009 renders for AS 7. **DEFERRED 2026-06-02**: requires running both services locally; cannot be performed in the implementing environment. User to verify locally or via the CI deploy after T014.

- [X] T012 [US1] Spot-check SC-004 (search input in global header on every page). Run `Select-String -Path src/frontend/templates/*.html -Pattern 'template "header"'` and confirm every page-rendering template (`home`, `cart`, `product`, `order`, `assistant`, `search`, `error`) includes the header partial. Partial templates (`ad.html` text_ad, `footer.html`, `header.html`, `recommendations.html`) correctly don't include it themselves. **Verified 2026-06-02**: all 7 page templates include `{{ template "header" . }}`; 4 partials correctly don't.

**Checkpoint**: User Story 1 is fully implemented and tested. The slice MVP is complete. Demoable locally.

---

## Phase 4: Polish & Deploy

**Purpose**: Get the slice onto the deploy path defined by TC-008 (CI deploys whatever lands on `attendee/matthew-buckland`).

- [X] T013 Commit the slice on `008-product-search` with a single commit. Stage exactly: `src/productcatalogservice/product_catalog_test.go`, `src/frontend/templates/search.html`, the entire `specs/008-product-search/` directory, and `CLAUDE.md`. Do NOT stage `src/productcatalogservice/product_catalog.go` (it is unchanged in this slice — that is the verification from T002). Commit message: `feat(search): empty-state UI + test coverage for name-or-description search (slice 008)`. Push with `--set-upstream origin 008-product-search`.

- [ ] T014 Merge `008-product-search` into `attendee/matthew-buckland` (TC-008 deploy path). Use `git checkout attendee/matthew-buckland; git merge --no-ff 008-product-search; git push`. After the push, CI will deploy. Do NOT touch `cloudbuild.yaml`, `skaffold.yaml`, GitHub Actions, Helm, Kustomize, or any infra config (TC-006 / TC-007).

---

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1 (Setup, T001)**: no dependencies — start here.
- **Phase 2 (Foundational, T002)**: depends on T001.
- **Phase 3 (US1, T003–T012)**: depends on T002 (foundational check must pass).
- **Phase 4 (Polish, T013–T014)**: depends on T010, T011, T012 (everything verified).

### Within Phase 3

- **T003** (fixtures) blocks T004–T008 (they assert against the new fixtures).
- **T004 → T005 → T006 → T007 → T008** are sequential because they all edit `product_catalog_test.go`.
- **T009** (template) is independent of T003–T008 and **can be done in parallel** with them.
- **T010** (run tests) depends on T003–T008.
- **T011** (manual verification) depends on T009 + T010.
- **T012** (SC-004 spot-check) is independent of all other US1 tasks (read-only inspection) — could be done any time after T002.

### Parallel opportunities

- **T009 ∥ {T003..T008}**: the template change is a completely separate file from the test file. A second engineer (or a parallel agent) can do T009 while T003–T008 are in flight.
- **T012** can also run any time after T002 — it's read-only.
- Everything else is sequential due to shared-file constraints.

---

## Parallel Example: User Story 1

```bash
# After T002 has passed, two streams can run side by side:

# Stream A — tests on product_catalog_test.go (sequential within the stream):
Task: "T003 — Extend TestMain mock catalog"
Task: "T004 — Add positive substring/case tests"
Task: "T005 — Add multi-match + de-duplication tests"
Task: "T006 — Add description-only regression guard"
Task: "T007 — Add negative / scope-bounding tests"
Task: "T008 — Add natural-order test"
Task: "T010 — Run go test, confirm all pass"

# Stream B — template change (independent file):
Task: "T009 — Add zero-results empty-state branch to search.html"

# Stream C — read-only spot check (independent):
Task: "T012 — Spot-check SC-004 via grep"

# Convergence:
Task: "T011 — Manual verification of all acceptance scenarios"
```

---

## Implementation Strategy

### MVP first (this slice IS the MVP)

This whole feature is one P1 user story. The MVP scope is everything in Phase 3. There is no Phase 2/3/N "later increment" — that's by design (the spec's Out of Scope section enumerates 15 things explicitly excluded from the slice).

1. T001 — Setup verification.
2. T002 — Foundational verification (existing code matches amended spec).
3. T003–T012 — Implement and verify User Story 1.
4. **Stop and validate** with manual scenarios + `go test`.
5. T013–T014 — Commit and deploy via merge.

### What's deliberately NOT in this task list

Per the spec's Out of Scope section and `plan.md`'s "Open follow-ups":

- No frontend handler tests (`src/frontend/` has no test directory; adding the first ever frontend test is out of scope).
- No soft-error UX for the catalog-service-down case (FR-008 follow-up #2 in `plan.md`).
- No proto edits, no `genproto/` regeneration, no Dockerfile / Helm / Kustomize / Terraform / GitHub Actions changes (TC-005–TC-007).
- No new metrics, no Segment / Snowplow / GA4 wiring (Out of Scope).
- No typo tolerance, ranking, pagination, autocomplete, suggestions (Out of Scope).
- No `/api/search` JSON endpoint, no as-you-type live results (Out of Scope).

If any of these come up during implementation, stop and amend the spec — don't deviate during implementation. That's the rule we already used to handle the name-only-vs-name-OR-description question.

---

## Notes

- **Net code surface of this slice**: one test file extended (~80–120 new lines of test code, depending on how compactly the table-driven tests are written) and one template file edited (~5 new lines). **Zero production Go code changes.**
- **The regression guard test (T006) is the single most important new test in this slice.** It is the workshop's anti-pattern detector for the recurring "search-misses-descriptions" seed bug.
- Commit after T012 succeeds; do not stage `product_catalog.go`.
- Verify with `git diff --stat origin/main` before pushing that the file list matches "Done When" in `quickstart.md`.
