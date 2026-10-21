# Ground truth — bug_01_shipping_cost_nanos_truncation

## Bug status
**Planted and currently live in source.** File already modified:
`src/shippingservice/main.go`, line 135.

## Root cause (plain English)
Any customer who places an order sees a shipping cost of **$8.10** on the order
confirmation page, even though the shop's flat shipping rate is **$8.99**. The
price is wrong by exactly the same amount every time — it isn't random or
currency-specific, it's always off in the same way.

## Root cause (technical)
`shippingservice` represents money as two integers: whole units (dollars) and
"nanos" — billionths of a unit, used so the services never have to deal with
floating-point rounding. Since 1 dollar = 1,000,000,000 nanos, 1 cent must be
converted using the constant `10,000,000` (1 cent = 1/100 dollar = 10,000,000
nanos).

In `GetQuote` (`src/shippingservice/main.go:135`), the cents-to-nanos conversion
uses the wrong constant:

```go
Nanos: int32(quote.Cents * 10000000)
```

was changed to:

```go
Nanos: int32(quote.Cents * 1000000)
```

— missing a zero, making the conversion exactly **10× too small**. For the flat
rate of $8.99 (`Dollars=8, Cents=99`), the correct nanos value is
`99 * 10,000,000 = 990,000,000` (→ $8.99). With the bug, it computes
`99 * 1,000,000 = 99,000,000` (→ $8.099, which rounds/truncates for display to
**$8.10**).

Nothing downstream (checkoutservice's currency conversion, the frontend's
`MoneyFormatter`) is at fault — they correctly render whatever
`shippingservice` sends them. The money leaves `shippingservice` already wrong.

## Why this is hard to spot
The function still "looks" correct at a glance — it's a single multiplication
by a constant that reads as plausible shorthand for a unit conversion. The bug
only reveals itself by knowing the specific invariant that 1 cent = 10,000,000
nanos in this protocol, and by actually computing the arithmetic rather than
pattern-matching the code shape.
