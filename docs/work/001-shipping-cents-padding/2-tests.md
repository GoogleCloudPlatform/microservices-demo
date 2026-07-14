# 001 — Shipping quote cents padding — Test Spec

**Behaviour under test:** `Quote.String()` in `src/shippingservice/quote.go` must always render
the cents field as exactly two digits, in the form `$<dollars>.<cc>`. The bug it pins down: the
current format verb drops the leading zero for cents values below 10 (e.g. rendering `$8.5`
instead of `$8.05`). These scenarios describe the *observable output* only — they do not name or
depend on any particular format verb or implementation technique.

## In scope

- The string returned by `Quote.String()` across the full range of `Cents` behaviour that matters:
  a normal two-digit cents value, a cents value below 10 (the leading-zero case that is currently
  broken), a zero quote, and the dollars-zero / single-digit-cents boundary.

## Out of scope

- The gRPC money conversion in `src/shippingservice/main.go` (`GetQuote` builds `pb.Money` from
  `quote.Dollars` / `quote.Cents` directly, not via `String()`; already correct and unaffected by
  this bug).
- The quote *calculation* logic (`CreateQuoteFromFloat`, `CreateQuoteFromCount`) — only the string
  rendering of an already-constructed `Quote` is under test here.
- The proto definitions, service configuration, and build tooling.

## Seams

None. `Quote.String()` is a pure, deterministic, in-memory method on a value type (`Quote{Dollars,
Cents uint32}`) with no I/O — no database, HTTP call, queue, clock, or randomness involved. No
mocks, fakes, or stubs are needed or applicable; every scenario below is a plain input/output
assertion, executable directly as a Go table-driven test.

## Scenarios

### T-001 — Two-digit cents render unchanged (happy path)

- **Given** a `Quote{Dollars: 8, Cents: 99}`
- **When** `.String()` is called
- **Then** the result is `"$8.99"`

This is the pre-existing regression case (today's `TestQuoteString`): cents already occupying two
digits must continue to render correctly and must stay green after the fix.

### T-002 — Cents below 10 are zero-padded to two digits (edge, leading-zero — the core bug)

- **Given** a `Quote{Dollars: 8, Cents: 5}`
- **When** `.String()` is called
- **Then** the result is `"$8.05"` (not `"$8.5"`)

This is the primary bug this unit fixes: a single-digit cents value must never be rendered with
only one digit.

### T-003 — Zero quote renders as two zero digits for cents (edge)

- **Given** a `Quote{Dollars: 0, Cents: 0}`
- **When** `.String()` is called
- **Then** the result is `"$0.00"` (not `"$0.0"`)

### T-004 — Zero dollars with single-digit cents (edge)

- **Given** a `Quote{Dollars: 0, Cents: 9}`
- **When** `.String()` is called
- **Then** the result is `"$0.09"` (not `"$0.9"`)

Confirms the leading-zero padding applies to cents regardless of the dollars value, while dollars
themselves are never zero-padded (out of scope to test further — only cents width is a rule here).

## Coverage note

Four scenarios are sufficient and non-redundant: T-001 pins the already-correct two-digit case
(regression guard), T-002 pins the core reported bug, and T-003/T-004 cover the two zero-adjacent
boundaries (both fields zero; dollars zero with nonzero single-digit cents). No further cases are
needed — adding more (e.g. varying dollars width) would test behaviour this unit does not change.
