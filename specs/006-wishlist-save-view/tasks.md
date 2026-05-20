# Tasks: Wishlist — Save a Product for Later and View the Saved List

**Input**: Design documents from `specs/006-wishlist-save-view/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/http-routes.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.
**Tests**: Not requested in the feature specification — no test tasks included.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete-task dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Add the wishlist cookie constant that all subsequent phases depend on.

- [x] T001 Add `cookieWishlist = cookiePrefix + "wishlist"` constant to `src/frontend/main.go` alongside the existing `cookieRecentlyViewed` constant

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Cookie helper functions and common template data injection that ALL user story phases require.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T002 Add `wishlistFromCookie(r *http.Request) []string` helper to `src/frontend/handlers.go` — mirrors `recentlyViewedFromCookie`; reads `cookieWishlist`, splits on `|`, returns slice of product IDs
- [x] T003 Add `updateWishlist(existing []string, id string) []string` helper to `src/frontend/handlers.go` — prepends id, deduplicates (keeping first occurrence), no size cap; mirrors `updateRecentlyViewed`
- [x] T004 Update `injectCommonTemplateData` in `src/frontend/handlers.go` to compute and inject `"wishlist_size": len(wishlistFromCookie(r))` so every page render has the wishlist item count available for the header badge

**Checkpoint**: Cookie helpers and common data injection are complete — user story phases can begin.

---

## Phase 3: User Story 1 — Save a Product for Later (Priority: P1) 🎯 MVP

**Goal**: A shopper on a product detail page can click "Save for later", the product is added to their wishlist cookie, and they see an inline confirmation.

**Independent Test**: Visit `/product/{id}`, click "Save for later", confirm `?saved=1` redirect and the confirmation banner appear; check the `shop_wishlist` cookie contains the product ID.

- [x] T005 [US1] Add `saveToWishlistHandler` to `src/frontend/handlers.go`:
  - Read `product_id` from POST form value; return 400 if empty
  - Call `wishlistFromCookie(r)` → `updateWishlist(existing, productID)` → write updated `shop_wishlist` cookie (`MaxAge: cookieMaxAge`)
  - Redirect to `/product/{product_id}?saved=1`
- [x] T006 [US1] Register `r.HandleFunc(baseUrl+"/wishlist", svc.saveToWishlistHandler).Methods(http.MethodPost)` in `src/frontend/main.go`
- [x] T007 [US1] Update `productHandler` in `src/frontend/handlers.go` to pass two new keys to the template:
  - `"in_wishlist"`: boolean — checks whether `product.Item.Id` is in `wishlistFromCookie(r)`
  - `"just_saved"`: boolean — checks whether `r.URL.Query().Get("saved") == "1"`
- [x] T008 [US1] Update `src/frontend/templates/product.html` — inside the `product-wrapper` div, below the existing "Add To Cart" form, add:
  - A `<form method="POST" action="{{ $.baseUrl }}/wishlist">` with hidden `product_id` field and a submit button that reads "Save for later" normally or "Saved ✓" when `$.in_wishlist` is true (button disabled when already saved)
  - A conditional inline confirmation banner: `{{ if $.just_saved }}<div class="cymbal-banner">Saved to your wishlist</div>{{ end }}`

**Checkpoint**: US1 is fully functional. Saving a product works end-to-end; confirmation banner shows; duplicate saves are no-ops.

---

## Phase 4: User Story 2 — View the Saved List (Priority: P2)

**Goal**: A shopper can navigate to their wishlist via a header icon and see each saved product with its name, image, and price. An empty-state message is shown when the list is empty.

**Independent Test**: Save one product, click the wishlist icon in the header, confirm the wishlist page shows that product with name, image, and price. Then navigate to `/wishlist` with an empty wishlist and confirm the empty-state message appears.

- [x] T009 [US2] Add `viewWishlistHandler` to `src/frontend/handlers.go`:
  - Read wishlist IDs from `wishlistFromCookie(r)`
  - For each ID, call `fe.getProduct` + `fe.convertCurrency` (same pattern as `viewCartHandler`)
  - Build `[]wishlistItemView{Item *pb.Product; Price *pb.Money}` slice
  - Render `wishlist` template with `"items"`, `"wishlist_size"`, `"cart_size"`, `"show_currency": true`, `"currencies"`
- [x] T010 [US2] Register `r.HandleFunc(baseUrl+"/wishlist", svc.viewWishlistHandler).Methods(http.MethodGet, http.MethodHead)` in `src/frontend/main.go` (add before the POST handler registered in T006)
- [x] T011 [US2] Create `src/frontend/templates/wishlist.html` with:
  - `{{ define "wishlist" }}` … `{{ template "header" . }}` / `{{ template "footer" . }}`
  - Main content: page heading "Your Wishlist", then either the empty-state `<p>` ("You haven't saved anything yet.") when `len $.items == 0`, or a product grid matching the visual style of the cart page (`cart.html`)
  - Each item card shows: product thumbnail (`$.baseUrl + item.Item.Picture`), product name, and formatted price (`renderMoney item.Price`)
- [x] T012 [P] [US2] Update `src/frontend/templates/header.html` — inside the `.controls` div, immediately before the cart `<a class="cart-link">` tag, add:
  ```html
  <a href="{{ $.baseUrl }}/wishlist" class="cart-link">
      <span class="material-symbols-outlined" style="font-size:22px;" title="Wishlist">bookmarks</span>
      {{ if $.wishlist_size }}
      <span class="cart-size-circle">{{$.wishlist_size}}</span>
      {{ end }}
  </a>
  ```
  *(The Google Symbols font is already loaded in the `<head>`; `cart-size-circle` reuses the existing badge style.)*

**Checkpoint**: US2 is fully functional. The wishlist icon appears in the header on all pages. Navigating to `/wishlist` shows saved items or the empty-state message.

---

## Phase 5: User Story 3 — Session Scope (Priority: P3)

**Goal**: The wishlist is session-scoped — it is empty at the start of every new browser session and survives navigation within the same session.

**Independent Test**: Save products, close the browser tab, open a new session, confirm the wishlist is empty. Separately: save products, navigate away and back within the same session, confirm items are still present.

- [x] T013 [US3] Verify in `saveToWishlistHandler` (`src/frontend/handlers.go`) that the `shop_wishlist` cookie is written with `MaxAge: cookieMaxAge` (48 h) — consistent with `shop_recently-viewed` and the Assumptions in the spec. Add a code comment explaining the 48-hour lifetime aligns with the session-only intent documented in `specs/006-wishlist-save-view/spec.md`.
- [x] T014 [US3] Confirm no server-side wishlist state exists: verify `viewWishlistHandler` and `saveToWishlistHandler` read and write only the `shop_wishlist` cookie — no in-memory map, no calls to external services, no new fields on `frontendServer`.

**Checkpoint**: All three user stories are complete and independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T015 [P] Review `src/frontend/templates/wishlist.html` for visual consistency with `src/frontend/templates/cart.html` — ensure product card layout, typography, and spacing match the existing store aesthetic
- [x] T016 [P] Check `src/frontend/static/styles/styles.css` — add a `.cymbal-banner` style (green background, white text, padding) for the save-confirmation banner added in T008 if no equivalent class exists
- [ ] T017 Run the quickstart verification steps from `specs/006-wishlist-save-view/quickstart.md` end-to-end against a locally running frontend to confirm all acceptance criteria pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T001 — blocks all user story phases
- **US1 (Phase 3)**: Depends on Phase 2 completion (T002, T003, T004)
- **US2 (Phase 4)**: Depends on Phase 2 completion; T012 (header icon) is independent of T009–T011 and can run in parallel with them
- **US3 (Phase 5)**: Depends on Phase 3 completion (save handler must exist to verify)
- **Polish (Phase 6)**: Depends on Phase 4 completion (template must exist to review)

### User Story Dependencies

- **US1 (P1)**: Requires Foundational phase only — no dependency on US2 or US3
- **US2 (P2)**: Requires Foundational phase only — T012 (header icon) can be done in parallel with T009–T011
- **US3 (P3)**: Logically requires US1 (the save mechanism must exist to verify session scope)

### Within Each Phase

- T002 and T003 are independent and can be written together
- T004 depends on T002 (calls `wishlistFromCookie`)
- T005 depends on T002 and T003 (uses both helpers)
- T006 depends on T005 (registers the handler)
- T007 depends on T002 (calls `wishlistFromCookie`)
- T008 depends on T007 (uses `in_wishlist` and `just_saved` template vars)
- T009 depends on T002 (calls `wishlistFromCookie`)
- T010 depends on T009 (registers the handler)
- T011 and T012 are independent of each other and can be done in parallel

### Parallel Opportunities

Within Phase 2: T002 and T003 can be written in one pass (same file, no mutual dependency).
Within Phase 4: T012 (header.html) can be worked on in parallel with T009–T011 (handlers.go + wishlist.html) since they are in different files.
Within Phase 6: T015 and T016 are in different files and can be done in parallel.

---

## Parallel Example: Phase 4 (User Story 2)

```
In parallel:
  Task T009 — viewWishlistHandler in src/frontend/handlers.go
  Task T011 — wishlist.html template in src/frontend/templates/
  Task T012 — wishlist icon in src/frontend/templates/header.html

Then sequentially:
  Task T010 — register GET /wishlist route (depends on T009)
```

---

## Implementation Strategy

### MVP (User Story 1 Only — Phases 1–3)

1. Complete Phase 1: add cookie constant (T001)
2. Complete Phase 2: cookie helpers + common data injection (T002–T004)
3. Complete Phase 3: save handler, route, PDP button, confirmation banner (T005–T008)
4. **STOP AND VALIDATE**: Save a product from the PDP, verify cookie is set, verify confirmation banner appears, verify duplicate save is a no-op
5. Ship / demo — the wishlist saves correctly even before the view page exists

### Incremental Delivery

1. Phases 1–3 → US1 complete → demo save flow
2. Phase 4 → US2 complete → demo full wishlist (save + view + header icon)
3. Phase 5 → US3 verified → session scope confirmed
4. Phase 6 → Polish complete → ready for code review

---

## Notes

- [P] tasks = different files or no shared state, safe to run in parallel
- [Story] label maps each task to a user story for traceability
- All helpers follow the existing `recentlyViewed*` pattern — read the adjacent code before implementing
- The `renderMoney` template function and `pb.Money` type are already available — reuse them in `wishlist.html`
- No new Go packages or modules are needed
- No new SVG icons needed — Google Symbols font already loaded in `header.html`
