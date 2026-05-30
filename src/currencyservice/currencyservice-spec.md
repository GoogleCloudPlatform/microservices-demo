# currencyservice-spec.md

Source-of-truth specification for reimplementing `currencyservice` in C++.
Derived from the Node.js implementation in `src/currencyservice/`.

---

## 1. Service Purpose

`currencyservice` is a gRPC microservice in the Online Boutique (Hipster Shop)
demo application. It serves two business functions:

- **Currency listing** — return the set of ISO 4217 currency codes the service
  can work with.
- **Currency conversion** — convert a monetary amount expressed as a `Money`
  proto from one currency to another, using EUR as the pivot/intermediate
  currency.

The service is stateless at the request level; all exchange-rate data is loaded
from a static JSON file bundled inside the container image. No external network
calls are made during normal operation.

---

## 2. API Contract

### 2.1 Proto packages and files

| File | Package |
|---|---|
| `proto/demo.proto` | `hipstershop` |
| `proto/grpc/health/v1/health.proto` | `grpc.health.v1` |

### 2.2 `hipstershop.CurrencyService`

#### `GetSupportedCurrencies`

```protobuf
rpc GetSupportedCurrencies(Empty) returns (GetSupportedCurrenciesResponse) {}
```

| Direction | Message | Fields |
|---|---|---|
| Request | `Empty` | _(none)_ |
| Response | `GetSupportedCurrenciesResponse` | `repeated string currency_codes = 1` |

Returns the list of 3-letter ISO 4217 codes for which exchange rates are
available. Derived at runtime from the keys of `currency_conversion.json`
(currently 33 currencies; see §4).

#### `Convert`

```protobuf
rpc Convert(CurrencyConversionRequest) returns (Money) {}
```

| Direction | Message | Fields |
|---|---|---|
| Request | `CurrencyConversionRequest` | `Money from = 1`, `string to_code = 2` |
| Response | `Money` | `string currency_code = 1`, `int64 units = 2`, `int32 nanos = 3` |

Converts the amount in `from` to the currency identified by `to_code`.
Returns a `Money` whose `currency_code` equals `to_code`.

#### `Money` message (shared type)

```protobuf
message Money {
    string currency_code = 1;   // ISO 4217, e.g. "USD"
    int64  units = 2;           // whole monetary units
    int32  nanos = 3;           // fractional units * 10^9
                                // range: -999,999,999 .. +999,999,999
}
```

Sign rules (from proto comments):
- If `units > 0`, `nanos` must be ≥ 0.
- If `units == 0`, `nanos` may be any sign.
- If `units < 0`, `nanos` must be ≤ 0.

### 2.3 `grpc.health.v1.Health`

```protobuf
rpc Check(HealthCheckRequest) returns (HealthCheckResponse);
```

The handler always responds with `status = SERVING` without inspecting the
request's `service` field or checking any internal state.

---

## 3. Core Business Logic

### 3.1 Exchange-rate data model

`data/currency_conversion.json` maps each currency code to its exchange rate
**relative to EUR** — i.e., how many units of that currency equal 1 EUR.

```json
{
  "EUR": "1.0",
  "USD": "1.1305",
  "JPY": "126.40",
  ...
}
```

All rates are stored as strings in the JSON file but are used as floating-point
numbers in arithmetic. The data is sourced from the European Central Bank.
EUR itself is present with a rate of `"1.0"`.

### 3.2 `_carry` — decimal normalization

```
_carry(amount):
    fractionSize = 10^9
    amount.nanos  += (amount.units % 1) * fractionSize   // move fractional units into nanos
    amount.units   = floor(amount.units) + floor(amount.nanos / fractionSize)  // carry nanos overflow into units
    amount.nanos   = amount.nanos % fractionSize          // keep remainder
    return amount
```

Purpose: after floating-point multiplication or division, `units` may have a
fractional part and `nanos` may exceed `10^9`. `_carry` normalizes both fields.

### 3.3 `Convert` algorithm

Given `from` (Money) and `to_code` (string):

**Step 1 — convert from source currency to EUR**

```
rate_from = data[from.currency_code]          // units of from-currency per EUR
euros.units = from.units / rate_from
euros.nanos = from.nanos / rate_from
euros = _carry(euros)
euros.nanos = round(euros.nanos)              // nearest integer (Math.round)
```

**Step 2 — convert from EUR to target currency**

```
rate_to = data[to_code]                       // units of to-currency per EUR
result.units = euros.units * rate_to
result.nanos = euros.nanos * rate_to
result = _carry(result)
result.units = floor(result.units)            // truncate towards zero
result.nanos = floor(result.nanos)            // truncate towards zero
result.currency_code = to_code
return result
```

**Rounding policy summary:**

| Step | Operation |
|---|---|
| After step 1 `_carry` | `Math.round(euros.nanos)` |
| After step 2 `_carry` | `Math.floor(result.units)`, `Math.floor(result.nanos)` |

### 3.4 `GetSupportedCurrencies` algorithm

Return `Object.keys(data)` — the list of currency codes present in the JSON
file, in insertion order (JSON key order as parsed by V8). No sorting is
applied by the server.

---

## 4. Dependencies

### 4.1 External services called

None. The service makes no outbound network calls during normal request handling.

### 4.2 Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `PORT` | **Yes** | _(none; crashes if absent)_ | TCP port the gRPC server binds on. Kubernetes manifests set this to `7000`. |
| `DISABLE_PROFILER` | No | unset | If set to any non-empty value, Google Cloud Profiler is not started. |
| `ENABLE_TRACING` | No | unset | Set to `"1"` to enable OpenTelemetry trace export. |
| `COLLECTOR_SERVICE_ADDR` | No | unset | URL of the OTLP gRPC trace collector. Used only when `ENABLE_TRACING=1`. |
| `OTEL_SERVICE_NAME` | No | `"currencyservice"` | Service name label in OpenTelemetry traces. |

### 4.3 Static data file

`data/currency_conversion.json` — bundled inside the container image at build
time. Contains 33 currency exchange rates vs. EUR. The file is loaded via
Node.js `require()`, which means it is parsed once and cached for the lifetime
of the process; there is no hot-reload mechanism.

### 4.4 Key npm dependencies

| Package | Version | Role |
|---|---|---|
| `@grpc/grpc-js` | 1.14.3 | gRPC server runtime |
| `@grpc/proto-loader` | 0.8.0 | Runtime proto file loading |
| `pino` | 10.3.1 | Structured JSON logging |
| `@google-cloud/profiler` | 6.0.4 | GCP continuous profiling (optional) |
| `@opentelemetry/sdk-node` | 0.214.0 | OTel tracing SDK (optional) |
| `@opentelemetry/exporter-otlp-grpc` | 0.26.0 | OTLP gRPC trace export |
| `@opentelemetry/instrumentation-grpc` | 0.214.0 | Auto-instrument gRPC calls for trace propagation |

### 4.5 Proto loading

Protos are loaded at startup with `protoLoader.loadSync` using these options:

```js
{ keepCase: true, longs: String, enums: String, defaults: true, oneofs: true }
```

`keepCase: true` means proto field names are used as-is (snake_case), not
camelCased. In the C++ reimplementation, proto field accessors follow the
standard Protobuf C++ naming conventions.

---

## 5. Data Flow

### 5.1 Server startup

1. Check `DISABLE_PROFILER`; start Google Cloud Profiler if not disabled.
2. Register gRPC OpenTelemetry instrumentation (always, for trace context propagation).
3. Check `ENABLE_TRACING`; if `"1"`, configure and start the OTel SDK with the
   OTLP gRPC exporter pointed at `COLLECTOR_SERVICE_ADDR`.
4. Load `demo.proto` and `health.proto` from disk.
5. Create a `grpc.Server`, register `CurrencyService` and `Health` services.
6. Bind on `[::]:${PORT}` with insecure credentials (no TLS).
7. Start serving.

### 5.2 `GetSupportedCurrencies` request

```
Client                          currencyservice
  |                                   |
  |-- GetSupportedCurrencies(Empty) ->|
  |                                   |-- require('./data/currency_conversion.json')
  |                                   |   (cached after first load)
  |                                   |-- Object.keys(data) -> ["EUR","USD","JPY", ...]
  |<-- GetSupportedCurrenciesResponse |
  |    { currency_codes: [...] }      |
```

### 5.3 `Convert` request

```
Client                                    currencyservice
  |                                            |
  |-- Convert({ from: {USD, 300, 0},           |
  |             to_code: "EUR" })  ----------->|
  |                                            |-- load data (cached)
  |                                            |-- euros = _carry({
  |                                            |     units: 300 / 1.1305,
  |                                            |     nanos: 0   / 1.1305
  |                                            |   })
  |                                            |-- euros.nanos = round(euros.nanos)
  |                                            |-- result = _carry({
  |                                            |     units: euros.units * 1.0,
  |                                            |     nanos: euros.nanos * 1.0
  |                                            |   })
  |                                            |-- result.units = floor(result.units)
  |                                            |-- result.nanos = floor(result.nanos)
  |                                            |-- result.currency_code = "EUR"
  |<-- Money { "EUR", 265, 367543 }  ----------|
```

### 5.4 `Check` (health) request

```
Client                    currencyservice
  |                            |
  |-- Check({}) -------------->|
  |<-- { status: SERVING } ----|
```

No internal checks are performed; the response is always `SERVING`.

---

## 6. Edge Cases and Error Handling

### 6.1 `Convert` error path

The entire `convert` handler body is wrapped in a `try/catch`:

```js
} catch (err) {
  logger.error(`conversion request failed: ${err}`);
  callback(err.message);   // BUG: passes string, not an Error/gRPC status
}
```

**Bug:** `callback(err.message)` passes a plain string as the first argument
instead of an `Error` object with a gRPC status code. The gRPC-js library
interprets a string error as a generic status 2 (UNKNOWN). The C++
reimplementation should use a proper gRPC `Status` with an appropriate code
(e.g., `INVALID_ARGUMENT` for bad input).

### 6.2 Unknown currency codes (unvalidated)

Neither `from.currency_code` nor `to_code` is validated against the known set
before use. If an unknown code is passed:

- `data[unknown_code]` evaluates to `undefined` in JavaScript.
- Division or multiplication by `undefined` yields `NaN`.
- `_carry` propagates `NaN` through all arithmetic without throwing.
- The callback is called with `{units: NaN, nanos: NaN, currency_code: to_code}`.
- The `try/catch` does **not** trigger because no exception is thrown.
- The gRPC response will contain `NaN` serialized as `0` for numeric proto
  fields (proto3 default), returning a silently incorrect zero-amount response.

**C++ recommendation:** validate both `from.currency_code` and `to_code` against
the data map before performing arithmetic; return `NOT_FOUND` or
`INVALID_ARGUMENT` status if either is absent.

### 6.3 Missing or null `from` field

If the client sends a `CurrencyConversionRequest` with `from` omitted, proto3
defaults apply and `from` will be a zeroed `Money`. Division of `0 / rate`
is `0`, so the conversion will return a zero `Money` rather than an error.

### 6.4 EUR-to-EUR conversion

Works correctly: dividing by `1.0` and multiplying by `1.0` leaves the value
unchanged (modulo floating-point rounding through `_carry`).

### 6.5 Negative amounts

The proto spec allows negative `Money` values (negative `units` with
correspondingly negative `nanos`). The `_carry` function uses `Math.floor`,
which rounds towards negative infinity. In JavaScript, `%` on negative numbers
preserves the sign of the dividend. The C++ implementation should be careful
to replicate this exact floor/remainder behavior for negative amounts, or
explicitly document that negative amounts are out of scope.

### 6.6 Large amounts and floating-point precision

`int64 units` can represent values up to ~9.2 × 10^18. JavaScript `Number`
(IEEE 754 double) has ~15–16 significant decimal digits. For large values of
`units`, the intermediate floating-point calculation will lose precision.
The C++ implementation may use integer arithmetic or 128-bit floats to improve
accuracy, but must document any behavioral difference.

### 6.7 Health check always reports SERVING

The `Check` handler unconditionally returns `SERVING`. It does not check
whether the JSON data file loaded successfully, whether the server is under
load, or any other internal signal. The C++ implementation should match this
behavior unless health-check semantics are explicitly improved.

### 6.8 Port misconfiguration

If `PORT` is unset or empty, `server.bindAsync('[::]:undefined', ...)` will
fail. The Node.js process logs the error and exits. The C++ implementation
should validate the port at startup and exit with a clear error message.

---

## 7. Test Coverage Gaps

`package.json` defines the test script as:

```json
"test": "echo \"Error: no test specified\" && exit 1"
```

**There are zero tests in this service.** The following behaviors have no
automated coverage and must be tested in the C++ reimplementation:

| Behavior | Priority |
|---|---|
| `GetSupportedCurrencies` returns all 33 expected currency codes | High |
| `Convert` USD → EUR with known rate produces correct result | High |
| `Convert` EUR → USD with known rate produces correct result | High |
| `Convert` non-EUR → non-EUR (two-step via EUR pivot) | High |
| `Convert` EUR → EUR (identity conversion) | High |
| `Convert` same source and target currency (identity) | High |
| `Convert` with unknown `from.currency_code` returns error | High |
| `Convert` with unknown `to_code` returns error | High |
| `Convert` with zero `units` and zero `nanos` | Medium |
| `Convert` with fractional `nanos` (non-zero nanos, zero units) | Medium |
| `Convert` carry propagation: nanos overflow into units after multiply | Medium |
| `Convert` carry propagation: fractional units folded into nanos | Medium |
| `Convert` negative `Money` amounts | Medium |
| `Convert` maximum `int64` `units` value (precision boundary) | Low |
| `Check` always returns `SERVING` | Low |
| Server startup fails cleanly when `PORT` is unset | Low |
| Server startup with `ENABLE_TRACING=1` and valid collector address | Low |

---

## 8. Supported Currencies (reference)

The following 33 currencies are in `currency_conversion.json` as of the
current commit. Rates are EUR-based (1 EUR = N units):

| Code | Rate | Code | Rate |
|---|---|---|---|
| EUR | 1.0 | HRK | 7.4210 |
| USD | 1.1305 | RUB | 74.4208 |
| JPY | 126.40 | TRY | 6.1247 |
| BGN | 1.9558 | AUD | 1.6072 |
| CZK | 25.592 | BRL | 4.2682 |
| DKK | 7.4609 | CAD | 1.5128 |
| GBP | 0.85970 | CNY | 7.5857 |
| HUF | 315.51 | HKD | 8.8743 |
| PLN | 4.2996 | IDR | 15999.40 |
| RON | 4.7463 | ILS | 4.0875 |
| SEK | 10.5375 | INR | 79.4320 |
| CHF | 1.1360 | KRW | 1275.05 |
| ISK | 136.80 | MXN | 21.7999 |
| NOK | 9.8040 | MYR | 4.6289 |
| | | NZD | 1.6679 |
| | | PHP | 59.083 |
| | | SGD | 1.5349 |
| | | THB | 36.012 |
| | | ZAR | 16.0583 |

---

*Generated 2026-05-29 from `src/currencyservice/` at commit `5096a85`.*
