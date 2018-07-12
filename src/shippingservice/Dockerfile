FROM golang:1.10-alpine as builder
RUN apk add --no-cache \
  ca-certificates \
  git
WORKDIR /src/microservices-demo/shippingservice
# get known dependencies
RUN go get -d golang.org/x/net/context \
  google.golang.org/grpc \
  google.golang.org/grpc/reflection \
  go.opencensus.io/exporter/stackdriver \
  go.opencensus.io/plugin/ocgrpc \
	go.opencensus.io/trace

COPY . .
# get other dependencies
RUN go get -d ./...
RUN go build -o /shippingservice .

FROM alpine as release
COPY --from=builder /shippingservice /shippingservice
ENV APP_PORT=50051
EXPOSE 50051
ENTRYPOINT ["/shippingservice"]
