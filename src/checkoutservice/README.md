# Checkout Service (Java)

A Java + gRPC reimplementation of the Online Boutique `checkoutservice`, ported from the original
Go service. It exposes `hipstershop.CheckoutService/PlaceOrder` and orchestrates calls to the cart,
product-catalog, currency, shipping, payment, and email services.

## Layout

```
build.gradle                 # protobuf plugin compiles src/main/proto -> Java + gRPC stubs
settings.gradle
Dockerfile                   # multi-stage: gradle build -> slim JRE
src/main/proto/hipstershop.proto # the official Online Boutique service contract
src/main/resources/log4j2.xml# structured (Stackdriver-shaped) JSON logging to stdout
src/main/java/hipstershop/
  CheckoutService.java        # main(): gRPC server, downstream channels, health service
  CheckoutServiceImpl.java    # PlaceOrder orchestration + coupon discount logic
  MoneyUtil.java              # fixed-point money arithmetic (port of Go money package)
```

The generated classes match the repo convention (proto `package hipstershop`, no `java_package`):
messages land in the outer class `hipstershop.Hipstershop` (e.g. `hipstershop.Hipstershop.PlaceOrderRequest`)
and service stubs in `hipstershop.CheckoutServiceGrpc`, `hipstershop.CartServiceGrpc`, etc.

## Build & run

```bash
./gradlew installDist            # compiles protos + Java, builds a runnable dist
./gradlew run                    # run locally (needs the env vars below set)
```

Docker:

```bash
docker build -t checkoutservice-java .
docker run -p 5050:5050 --env-file .env checkoutservice-java
```

## Configuration (environment variables)

| Variable                        | Required | Default | Purpose                          |
| ------------------------------- | -------- | ------- | -------------------------------- |
| `PORT`                          | no       | `5050`  | gRPC listen port                 |
| `CART_SERVICE_ADDR`             | yes      | —       | `host:port` of cartservice       |
| `PRODUCT_CATALOG_SERVICE_ADDR`  | yes      | —       | `host:port` of productcatalog    |
| `CURRENCY_SERVICE_ADDR`         | yes      | —       | `host:port` of currencyservice   |
| `SHIPPING_SERVICE_ADDR`         | yes      | —       | `host:port` of shippingservice   |
| `PAYMENT_SERVICE_ADDR`          | yes      | —       | `host:port` of paymentservice    |
| `EMAIL_SERVICE_ADDR`            | yes      | —       | `host:port` of emailservice      |

Any missing required variable causes an immediate startup failure (fail-fast), matching the Go
`mustMapEnv` behaviour.

## Notes on parity with the Go service

- Downstream channels are plaintext (`usePlaintext()`), matching the Go insecure credentials —
  transport security is expected from the service mesh, not the app.
- The coupon feature is preserved: `SAVE10` / `SAVE50` / `SAVE100` (whole-dollar USD discounts,
  converted to the user's currency), defaulting to `SAVE10` when no code is sent, and the charged
  total is floored at zero so payment never receives a negative amount.
- Money is handled with integer units + nanos (never floats) via `MoneyUtil`, a direct port of the
  Go `money` package's carry/sign normalization.
