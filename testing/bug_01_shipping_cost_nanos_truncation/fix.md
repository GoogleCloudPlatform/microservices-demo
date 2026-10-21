# Ground truth fix — bug_01_shipping_cost_nanos_truncation

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/shippingservice/main.go`

## Exact change

```diff
--- a/src/shippingservice/main.go
+++ b/src/shippingservice/main.go
@@ func (s *server) GetQuote(ctx context.Context, in *pb.GetQuoteRequest) (*pb.GetQuoteResponse, error) {
 	return &pb.GetQuoteResponse{
 		CostUsd: &pb.Money{
 			CurrencyCode: "USD",
 			Units:        int64(quote.Dollars),
-			Nanos:        int32(quote.Cents * 1000000)},
+			Nanos:        int32(quote.Cents * 10000000)},
 	}, nil
```

## Why this is correct
`Money.nanos` is defined (consistently with every other service in this
codebase, and with `google.type.Money`) as billionths of the currency's base
unit. One cent is one-hundredth of a dollar, i.e. `1,000,000,000 / 100 =
10,000,000` nanos. Restoring the `10000000` multiplier makes `quote.Cents * 10000000`
correctly represent the cents portion of the quote in nanos, so a flat quote of
$8.99 (`Dollars=8, Cents=99`) again serializes as `Money{units: 8, nanos:
990000000}` and renders as `$8.99` everywhere downstream.

No other file needs to change — `checkoutservice`'s currency conversion and the
frontend's rendering are both already correct; they were just faithfully
displaying the wrong number they received.
