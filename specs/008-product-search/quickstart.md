# Quickstart — Product Search (thin slice)

**Branch**: `008-product-search` | **Date**: 2026-06-02

This guide is for the engineer (human or agent) who will run `/speckit-tasks` and `/speckit-implement` next. It walks the slice end-to-end at a practical level: what to change, where, how to verify locally, and how to know you're done.

## What the slice is, in one paragraph

A header search bar already exists on every Online Boutique page. Submitting it goes to `/search?q=…` and renders results from `productcatalogservice.SearchProducts`. The spec for this slice defines the match semantics: **case-insensitive substring on `Product.name` OR `Product.description` — no other fields.** The existing backend already does exactly this; the slice's actual work is to add an explicit zero-results UI state, extend test coverage, and otherwise verify the existing implementation against the acceptance scenarios. That's the whole slice. No backend Go behavioural changes, no proto edits, no infra edits, no new files.

## Prerequisites

- This branch: `008-product-search` (currently checked out).
- Go toolchain matching the repo (`src/productcatalogservice/go.mod` and `src/frontend/go.mod`).
- Either:
  - **Local / Docker Compose / skaffold** — the existing dev tooling in this repo, OR
  - **GKE via the existing CI** — merge to `attendee/matthew-buckland` and let CI deploy (TC-008). For iterative development the local path is much faster.

No new tooling.

## Step-by-step

### 1. Confirm the existing match logic is what the spec asks for

```powershell
git log --oneline -3
# Expect:
#   642acab3 feat(frontend): add header search bar and /search results page
#   736cf79b fix(productcatalog): restore description match in SearchProducts
#   2371e659 training: seed bug (search-misses-descriptions)
```

The spec was amended (see `spec.md` → "Amendment") to define matching as case-insensitive substring on `name` OR `description`. The existing code at `src/productcatalogservice/product_catalog.go:60-72` already implements exactly that. **Do not modify the backend match logic.** If you find yourself touching `SearchProducts`, stop — that is not in this slice.

### 2. ~~Backend code change~~ — none required

The existing `SearchProducts` matches `name` OR `description` case-insensitively. The amended spec endorses this. **Skip to step 3.**

### 3. Extend the backend tests

`src/productcatalogservice/product_catalog_test.go`. Add products with **descriptions populated** (mock catalog currently has names only) and overlapping name substrings to `TestMain`'s mock catalog, then add table-driven tests covering the matrix in `research.md` R-4. Notably, `TestSearchProducts_DescriptionOnlyMatches` is the regression guard against re-introducing the seed bug, and `TestSearchProducts_CategoryOnlyDoesNotMatch` guards against scope creep into other fields.

Run:

```powershell
go test ./src/productcatalogservice/...
```

Expect: all existing tests pass; new tests pass; no test exercises the removed description arm.

### 4. Add the empty-state branch to the search template

`src/frontend/templates/search.html`. Replace the `{{ if $.query }} ... {{ else }} ... {{ end }}` block with a three-way split per `research.md` R-5: query-with-results, query-with-zero-results, no-query. The result is one extra `{{ if eq (len $.products) 0 }}` arm inside the existing query branch.

No Go code changes in the frontend.

### 5. Run the frontend locally to eyeball it

Build and run both services per the existing local dev path. Then manually verify each acceptance scenario in `spec.md`. A short cheat sheet:

| Scenario | Type into header search box | Expected on `/search?q=…` |
|---|---|---|
| AS 1 — exact name | `Vintage Typewriter` (any existing product name) | That product is in the results |
| AS 2 — substring | `typewriter` | Vintage Typewriter shows |
| AS 3 — uppercase | `VINTAGE` | Same result as `Vintage` |
| AS 5 — multi-match | A substring that appears in multiple product names | Multiple results |
| AS 6 — description match | A unique word that exists only in some `description` (check `products.json`) | That product IS in results |
| AS 6b — category-only must NOT match | A unique word that exists only in some `categories` value (check `products.json`) | That product is NOT in results |
| AS 7 — no matches | `zzzznonsense` | "No products found for …" empty state shown |
| AS 8 — empty submit | Click into the input, press Enter | No backend call, helper "Enter a term…" or equivalent shown |

(In the demo catalog the description-only word for AS 6 depends on which products are present; pick from `products.json` after the change.)

### 6. Header presence on every page

```powershell
# From the repo root
Select-String -Path .\src\frontend\templates\*.html -Pattern 'template "header"'
```

Every page-rendering template (`assistant`, `cart`, `error`, `home`, `order`, `product`, `search`) should include the header — confirmed as of 2026-06-02. Partial templates that correctly don't include the header: `ad.html` (text_ad partial), `footer.html`, `header.html` itself, `recommendations.html` (embedded in other pages). This is the SC-004 spot-check.

### 7. Commit and push

The slice is intentionally small enough for one commit. Note: `product_catalog.go` is NOT in the diff — only the test file, the template, and the spec artefacts.

```powershell
git add src/productcatalogservice/product_catalog_test.go `
        src/frontend/templates/search.html `
        specs/008-product-search/ `
        CLAUDE.md
git commit -m "feat(search): empty-state UI + test coverage for name-or-description search (slice 008)"
git push --set-upstream origin 008-product-search
```

### 8. Deploy via CI

CI deploys `attendee/matthew-buckland`. To get the slice into the deployed environment, merge `008-product-search` back into the attendee branch:

```powershell
git checkout attendee/matthew-buckland
git merge --no-ff 008-product-search
git push
```

CI picks it up from there. No new pipeline config. No new env vars. (TC-006, TC-007, TC-008.)

## How you know you're done

All of the following are true:

- [ ] `go test ./src/productcatalogservice/...` passes locally, including the new tests.
- [ ] Each acceptance scenario from `spec.md` is manually verified on the running storefront.
- [ ] Zero-result query renders an explicit "no products found" message.
- [ ] **`src/productcatalogservice/product_catalog.go` is unchanged** vs. the branch tip prior to this slice. (If you see it in `git diff`, you've touched something you shouldn't have.)
- [ ] No edits outside `src/productcatalogservice/product_catalog_test.go`, `src/frontend/templates/search.html`, `specs/008-product-search/`, and `CLAUDE.md`.
- [ ] No edits to `protos/demo.proto`, generated stubs, Dockerfiles, Helm, Kustomize, Terraform, GitHub Actions, `cloudbuild.yaml`, `skaffold.yaml`.
- [ ] `git diff origin/main --stat` shows only the files above, plus the `specs/008-product-search/` artefacts.

## Troubleshooting

- **Generated proto code drift.** If your editor or `genproto.sh` regenerates `genproto/*.go`, those changes are likely meaningless reformatting — verify with `git diff` and revert if so. The slice should leave `genproto/` untouched.
- **`TestSearchProducts` (existing) fails after the change.** Re-read its assertion (line 91-101) — it expects two `alpha` matches against two products named "Product Alpha One" and "Product Alpha Two". This is name-substring and should still pass. If it doesn't, the change probably affected something else.
- **Description match accidentally missing.** The `||` arm in `SearchProducts` is what makes description matching work. Confirm with `git grep -n 'product.Description' src/productcatalogservice/product_catalog.go` — should return exactly one hit, inside `SearchProducts`. If it returns zero, someone (probably you) deleted the description arm — restore it.
