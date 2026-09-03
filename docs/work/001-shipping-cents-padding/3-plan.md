# Plan: 001-shipping-cents-padding

**Inputs:** [1-research.md](./1-research.md), [2-tests.md](./2-tests.md)

**Summary:** Fix `Quote.String()` in `src/shippingservice/quote.go` so the cents field always
renders as two digits (zero-padded), replacing the format verb `%d` with `%02d`. The existing
`TestQuoteString` becomes a table-driven test covering all four scenarios in `2-tests.md`
(T-001..T-004), pinning the fix red-then-green.

**Commit convention:** Every task below is one atomic commit on the unit's branch
(`work/001-shipping-cents-padding`) per `docs/commit-conventions.md`; the unit ends with a squash
PR to `main` (team-reviewed, merged manually).

## Phases

### Phase 1 — Baseline
Confirm the tree builds/tests green before any change (orchestrator only, no dispatch).

### Phase 2 — Seams
None. `Quote.String()` already exists as a method on the existing `Quote` struct, and the existing
`TestQuoteString` already compiles against it — there is no interface, signature, or wiring gap to
scaffold before the tests can be written. No seam task is created for this unit.

### Phase 3 — Red tests
One batch: rewrite `TestQuoteString` into a table-driven test with the four rows from
`2-tests.md`. Expected-red, because T-002/T-003/T-004 fail under the current `"$%d.%d"` format
(only T-001 passes today).

### Phase 4 — Implementation
One batch, one feature area (the format string): change `quote.go:30` from `"$%d.%d"` to
`"$%d.%02d"`. This is the entire fix; the red table-driven test from Phase 3 goes green.

### Phase 5 — Consolidation
None needed. All four scenarios (T-001..T-004) are already covered by the single table-driven test
introduced in Phase 3 — there are no further edge/negative gaps or DRY cleanup to do. No
consolidation task is created for this unit.

### Phase 6 — E2E live smoke

Originally planned `e2e: n/a` — the fix only corrects an internal display/log string; the
client-facing gRPC shipping-quote money value is built from struct fields directly and is
unchanged, so `Quote.String()` is not on any live request path and the fix is not observable live.

At the user's request (a live cluster was available), a **regression smoke** was run instead: the
branch's `shippingservice` image (`shippingservice:work-001`) was deployed to the `kind-boutique`
cluster and the frontend browse → cart → checkout flow was driven end-to-end. Verdict **PASS** —
no regression in the shipping/checkout flow; evidence in `docs/test/001-shipping-cents-padding/`.
Note: this validates no-regression, **not** the cents-padding fix directly (nothing exercises
`Quote.String()` at runtime).

## Tasks

### P3-01: Verify baseline build+test green
- id: P3-01
- phase: baseline
- batch: B0
- mode: serial
- files touched: none (verification only)
- acceptance criterion: `go -C src/shippingservice build ./...` and `go -C src/shippingservice test ./...` both exit 0 on the unchanged tree
- maps-to test IDs: n/a
- expected-red: no
- high-risk: no

### P3-02: Table-driven TestQuoteString covering T-001..T-004
- id: P3-02
- phase: red-tests
- batch: B1
- mode: serial
- files touched: src/shippingservice/shippingservice_test.go
- acceptance criterion: `TestQuoteString` is rewritten as a table-driven test with rows {8,99}->"$8.99" (T-001), {8,5}->"$8.05" (T-002), {0,0}->"$0.00" (T-003), {0,9}->"$0.09" (T-004); `go -C src/shippingservice test ./...` fails on T-002/T-003/T-004 against the current implementation (expected-red)
- maps-to test IDs: T-001, T-002, T-003, T-004
- expected-red: yes
- high-risk: no

### P3-03: Zero-pad cents in Quote.String()
- id: P3-03
- phase: implementation
- batch: B2
- mode: serial
- files touched: src/shippingservice/quote.go
- acceptance criterion: `quote.go:30` format verb changed from `"$%d.%d"` to `"$%d.%02d"`; `go -C src/shippingservice build ./...` and `go -C src/shippingservice test ./...` both pass, including the table-driven `TestQuoteString` from P3-02 (all four rows green)
- maps-to test IDs: T-001, T-002, T-003, T-004
- expected-red: no
- high-risk: no

## TODO (work-execute consumes this)

### Batch B0 — baseline (orchestrator only, no dispatch)
- [x] P3-01 (baseline) verify build+test green

### Batch B1 — red tests (1 coder dispatch, serial) [expected-red]
- [x] P3-02 (red-tests) table-driven TestQuoteString covering T-001..T-004 -> maps T-001, T-002, T-003, T-004

### Batch B2 — implementation: cents zero-padding (1 coder dispatch, serial)
- [x] P3-03 (implementation) zero-pad cents in Quote.String() (`%d` -> `%02d`) -> maps T-001, T-002, T-003, T-004

### Batch B3 — e2e live regression smoke (1 e2e-tester dispatch)
- [x] P3-04 (e2e) regression smoke: deploy branch shippingservice, drive browse→cart→checkout -> evidence in docs/test/001-shipping-cents-padding/ (PASS)

> Originally `e2e: n/a` (Quote.String() is not on the live request path); run as a regression smoke at the user's request since a cluster was available. Proves no regression in the shipping/checkout flow, not the cents-padding fix directly.
