# Trainer cheat sheet — duplicate-recommendations

**Service:** `recommendationservice` (Python)
**File:** `src/recommendationservice/recommendation_server.py`
**Function:** `RecommendationService.ListRecommendations()`, line ~79.

## What the bug is

`random.sample(range(N), k)` was replaced with `random.choices(range(N), k=...)`.
`sample` draws *without* replacement; `choices` draws *with* replacement,
so duplicate indices are possible — and likely when the candidate pool is
small (current catalog has 9 products, after filtering out the one the
user is currently viewing it's 8, so duplicates appear ~50% of the time
across 5 picks by birthday-paradox math).

## What a good triage ticket looks like

- **Steps to reproduce:** open any product page → scroll to "You may
  also like" → refresh ~3-5 times → observe duplicate in the list.
  Same on the home-page recommendations widget.
- **Suspected area:** `recommendationservice`, the function that picks
  which product IDs to return. The "sometimes" pattern + small product
  catalog points at sampling-with-replacement rather than a logic error
  in upstream filtering.
- **Severity rationale:** UI quality issue, no money lost, no security
  impact. P3. Bunch this with other small UX fixes for the next sprint.
- **Note:** worth confirming with the data team whether the recommendation
  ranker downstream of this also assumes uniqueness — there may be no
  invariant being broken downstream, but worth checking.

## The actual fix

`random.sample(range(num_products), num_return)` — back to sample.
