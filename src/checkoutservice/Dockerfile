FROM golang:1.20-alpine as builder
RUN apk add --no-cache ca-certificates git

ENV PROJECT github.com/signalfx/microservices-demo/src/checkoutservice
WORKDIR /go/src/$PROJECT

COPY . .
ENV GO111MODULE on
RUN go build -o /go/bin/checkoutservice .

FROM alpine as release
RUN apk add --no-cache ca-certificates
RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe
COPY --from=builder /go/bin/checkoutservice /checkoutservice
EXPOSE 5050
ENTRYPOINT ["/checkoutservice"]
