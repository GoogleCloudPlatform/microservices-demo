# 001 — Shipping quote cents padding

**Summary:** `Quote.String()` in `src/shippingservice/quote.go` formats cents with `%d`, dropping the leading zero for cents < 10 (e.g. `$8.5` instead of `$8.05`); the fix is a two-digit, zero-padded cents field in the format string.

## Scope

**Is:** Fix the string/display formatting of `Quote.String()` so cents always render as two digits.

**Is NOT:** Touching the gRPC money conversion. The quoted money value returned to clients is built directly from `quote.Dollars` / `quote.Cents` in `main.go` (Units + Nanos) and is already correct — this bug never affects the actual money value, only the human-readable string used in logs/display. No change to the quote calculation, the proto, config, or build tooling.

## System slice

Components / files / seams touched:

- `src/shippingservice/quote.go:30` — the only line to change: `return fmt.Sprintf("$%d.%d", q.Dollars, q.Cents)`. Both `Dollars` and `Cents` are `uint32` (`quote.go:23-26`).
- Verified against `src/shippingservice/main.go:131-136` — `GetQuote` builds `pb.Money{Units: int64(quote.Dollars), Nanos: int32(quote.Cents * 10000000)}` from the fields directly; it does **not** call `String()`. Confirms the bug is display-only and the client-facing money value is unaffected.
- Verified against `src/shippingservice/shippingservice_test.go:199-206` — `TestQuoteString` only asserts `Quote{Dollars: 8, Cents: 99}` → `"$8.99"`, i.e. the two-digit case, so it cannot catch cents < 10.

## Stack & seams

- Go 1.26. Standard library `fmt` only (`quote.go` imports `fmt` and `math`).
- No external seam: no DB, HTTP, queue, or network boundary is involved in `Quote.String()`. It is a pure in-memory string-formatting method — there is no real external boundary to stub or integrate against.
- Build: `go -C src/shippingservice build ./...`. Test: `go -C src/shippingservice test ./...`.

## Unknowns / open questions

- Is `Quote.String()` used anywhere user-facing beyond logs? Determined: it is display/logging only. The client-facing money value comes from the struct fields directly (`main.go:131-136`), not from `String()`, so no user-facing money value depends on this method.
- The exhaustive set of `String()` call sites was not enumerated, but this does not change the fix: any caller wanting a `$D.CC` string benefits from two-digit cents, and no caller relies on the current single-digit behaviour for a numeric value.

## Findings & sources

- Go's `fmt` verb `%02d` zero-pads an integer to a minimum width of 2: the `0` flag pads with leading zeros rather than spaces, and the `2` sets the minimum field width. So `fmt.Sprintf("$%d.%02d", 8, 5)` → `"$8.05"` and `fmt.Sprintf("$%d.%02d", 0, 0)` → `"$0.00"`. This is canonical standard-library behaviour. Source: Go `fmt` package documentation, https://pkg.go.dev/fmt. No web browsing required.
- The fix is a single-line change to `quote.go:30`: replace `"$%d.%d"` with `"$%d.%02d"`. The existing `TestQuoteString` stays green (`{8,99}` → `"$8.99"` is unaffected) and should be extended to cover cents < 10 (`{8,5}` → `"$8.05"`) and zero (`{0,0}` → `"$0.00"`).

Task tier: lightweight — single file (quote.go), one Go service, no new seam or dependency, pinnable with 1–2 unit tests, no config/build-tooling change.
