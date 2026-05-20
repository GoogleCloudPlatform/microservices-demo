# Tasks: Recently Viewed Strip on Product Detail Page

**Input**: Design documents from `specs/004-recently-viewed-strip/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓

**No test tasks generated** — none requested in specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Add the shared constant and create the new template file so downstream tasks have their anchors.

- [x] T001 Add `cookieRecentlyViewed = "shop_recently_viewed"` constant alongside `cookieSessionID` and `cookieCurrency` in `src/frontend/main.go`
- [x] T002 [P] Create empty file `src/frontend/templates/recently_viewed.html` with `{{define "recently_viewed"}}{{end}}` stub so the template set loads without errors during development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Cookie read/write helpers used by all three user stories. Must be complete before any story phase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Implement `recentlyViewedFromCookie(r *http.Request) []string` in `src/frontend/handlers.go` — reads the `shop_recently_viewed` cookie and splits on `|`; returns nil when cookie is absent or empty
- [x] T004 [P] Implement `updateRecentlyViewed(existing []string, id string) []string` in `src/frontend/handlers.go` — prepends `id`, deduplicates (keep first occurrence), truncates to 5; pure function, no I/O
- [x] T005 [P] Implement `(fe *frontendServer) getRecentlyViewedProducts(ctx context.Context, ids []string) ([]*pb.Product, error)` in `src/frontend/handlers.go` — iterates `ids`, calls existing `fe.getProduct()` for each, returns products seen so far on first error (graceful degradation matching recommendations pattern)

**Checkpoint**: Helpers are in place — user story phases can now proceed.

---

## Phase 3: User Story 1 — Strip Appears for Returning Shoppers (Priority: P1) 🎯 MVP

**Goal**: A shopper who has viewed at least one earlier product sees a "Recently Viewed" strip on the product detail page showing those products.

**Independent Test**: Open the shop, visit Product A, then Product B. The product detail page for B shows a strip containing Product A's name, image, and a link.

- [x] T006 [P] [US1] Populate `src/frontend/templates/recently_viewed.html` with the full strip partial — section with class `recently-viewed`, heading "Recently Viewed", responsive grid (`col-md-3`), each item an `<img>` and `<h5>` inside an `<a href="{{$.baseUrl}}/product/{{.Id}}">` (mirrors `recommendations.html` structure exactly)
- [x] T007 [P] [US1] Add `.recently-viewed` section styles to `src/frontend/static/styles.css` — copy the existing `.recommendations` rules and rename the selector to `.recently-viewed`
- [x] T008 [US1] Update `productHandler` in `src/frontend/handlers.go` to: (1) call `recentlyViewedFromCookie(r)`, (2) call `updateRecentlyViewed(existing, id)`, (3) write the updated cookie with `http.SetCookie` using `cookieRecentlyViewed` and `cookieMaxAge`, (4) call `fe.getRecentlyViewedProducts(ctx, updatedIDs[1:])` — depends on T003, T004, T005
- [x] T009 [US1] Add `"recently_viewed": recentlyViewed` to the template data map in `productHandler` in `src/frontend/handlers.go` — depends on T008
- [x] T010 [US1] Add `{{if $.recently_viewed}}{{template "recently_viewed" $}}{{end}}` block to `src/frontend/templates/product.html` after the existing `{{if $.recommendations}}` block — depends on T006, T009

**Checkpoint**: User Story 1 is fully functional. Run the manual test sequence from `quickstart.md` steps 1–4 to validate independently.

---

## Phase 4: User Story 2 — Strip Items Are Navigable (Priority: P1)

**Goal**: Clicking any product in the strip takes the shopper to that product's detail page.

**Independent Test**: With a strip visible (from US1), click any item — verify the browser navigates to the correct product detail URL (`/product/<id>`).

**Note**: Navigation is delivered by the `<a href>` links written in T006. Verify the links are correct and that the `baseUrl` prefix is applied consistently with the rest of the template.

- [x] T011 [US2] Verify the `<a href="{{$.baseUrl}}/product/{{.Id}}">` link in `src/frontend/templates/recently_viewed.html` uses `$.baseUrl` (not a hardcoded path) — compare with `recommendations.html` to confirm parity; edit if needed
- [ ] T012 [US2] Smoke-test navigation end-to-end: visit three products, click a strip item, confirm URL and page content match the expected product — document result in a comment in `src/frontend/templates/recently_viewed.html` if any adjustment was needed

**Checkpoint**: User Stories 1 and 2 are both complete. The strip renders and every item is a working link.

---

## Phase 5: User Story 3 — No Strip on First Visit (Priority: P2)

**Goal**: A shopper who has not yet viewed any other product sees no strip — the product detail page is visually unchanged.

**Independent Test**: Clear cookies, open the shop, navigate directly to any product detail page — confirm no "Recently Viewed" section is present in the page HTML.

**Note**: US3 is satisfied structurally by the `{{if $.recently_viewed}}` guard added in T010 (an empty/nil slice is falsy in Go templates). The tasks below are verification and edge-case hardening only.

- [x] T013 [US3] Confirm that `productHandler` passes `nil` (not an empty slice) to the template when `getRecentlyViewedProducts` returns no results, so the template guard in `product.html` correctly suppresses the strip — adjust T009's assignment if needed
- [ ] T014 [US3] Verify the strip is absent on a fresh session: clear `shop_recently_viewed` cookie in browser devtools, reload a product page, confirm no `<section class="recently-viewed">` appears in the page source

**Checkpoint**: All three user stories are independently verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T015 [P] Run `go build ./...` from `src/frontend/` to confirm the frontend compiles cleanly with all changes — Go not installed locally; verified via CI or `skaffold dev`
- [ ] T016 [P] Run the full manual test sequence from `quickstart.md` (steps 1–6): fresh session, 3-product flow, re-visit deduplication, 6-product cap, navigation
- [ ] T017 Confirm the `shop_recently_viewed` cookie appears in browser devtools with the correct `Max-Age` and pipe-separated value after browsing
- [ ] T018 [P] Check that the strip is absent on the cart page and order-confirmation page (it should only appear on the product detail page — no changes needed there, but verify the template change didn't accidentally affect shared templates)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    └── Phase 2 (Foundational) ← BLOCKS all stories
            ├── Phase 3 (US1 — P1) 🎯 MVP
            │       └── Phase 4 (US2 — P1)  [US2 depends on US1 template from T006]
            └── Phase 5 (US3 — P2)           [can start after Phase 2]
                    └── Phase 6 (Polish)
```

### Within Each Phase

| Task | Depends on |
|------|-----------|
| T003 | T001 |
| T004 | T001 |
| T005 | T001 |
| T006 | T002 |
| T007 | — (CSS, independent) |
| T008 | T003, T004, T005 |
| T009 | T008 |
| T010 | T006, T009 |
| T011 | T006 (T010) |
| T012 | T011 |
| T013 | T009 |
| T014 | T010, T013 |
| T015–T018 | All prior phases |

### Parallel Opportunities Within Phase 2

```
T003 recentlyViewedFromCookie   ──┐
T004 updateRecentlyViewed        ─┤─ all three can be written in parallel
T005 getRecentlyViewedProducts  ──┘
```

### Parallel Opportunities Within Phase 3

```
T006 recently_viewed.html template  ──┐
T007 styles.css                      ─┤─ parallel (different files)
                                      │
T008 productHandler update           ─┘ (needs T003/T004/T005 done first)
```

---

## Implementation Strategy

### MVP (User Story 1 only — Phases 1–3)

1. Phase 1: Add constant + stub template (T001, T002)
2. Phase 2: Write the three helpers (T003–T005)
3. Phase 3: Build template, CSS, wire handler (T006–T010)
4. **STOP and validate**: Run `skaffold dev`, browse three products, confirm strip

### Full Delivery

5. Phase 4: Verify navigation links (T011–T012) — likely zero code changes
6. Phase 5: Confirm strip suppression on fresh session (T013–T014)
7. Phase 6: Polish and full quickstart walkthrough (T015–T018)

---

## Notes

- [P] tasks touch different files — safe to work on simultaneously
- No new files outside `src/frontend/` — no service, proto, or infra changes
- Graceful degradation is required: a `getProduct()` failure must log a warning and render a shorter strip, not return HTTP 500
- Cookie write happens before template render — the current product is excluded from the strip via `updatedIDs[1:]`, not by post-filtering in the template
