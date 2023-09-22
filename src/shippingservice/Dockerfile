FROM golang:1.20-alpine as builder
RUN apk add --no-cache ca-certificates git

ENV PROJECT github.com/signalfx/microservices-demo/src/shippingservice
WORKDIR /go/src/$PROJECT

COPY . .
ENV GO111MODULE on
RUN go build -o /go/bin/shippingservice .

FROM alpine as release
RUN apk add --no-cache ca-certificates
RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe
COPY --from=builder /go/bin/shippingservice /shippingservice
ENV APP_PORT=50051
EXPOSE 50051
ENTRYPOINT ["/shippingservice"]
