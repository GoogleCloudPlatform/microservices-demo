# Shipping Service

The Shipping service provides price quote, tracking IDs, and the impression of order fulfillment & shipping processes.

## Local

Now using Go 1.13 Modules. just use `go build`

## Build

From repository root, run:

```
docker build --file src/shippingservice/Dockerfile .
```

## Test

```
go test .
```
