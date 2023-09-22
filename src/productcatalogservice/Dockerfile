FROM golang:1.20-alpine AS builder
RUN apk add --no-cache ca-certificates git

ENV PROJECT github.com/signalfx/microservices-demo/src/productcatalogservice
WORKDIR /go/src/$PROJECT

COPY . .
ENV GO111MODULE on
RUN go build -o /go/bin/productcatalogservice .

FROM alpine AS release
RUN apk add --no-cache ca-certificates
RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe
WORKDIR /productcatalogservice
COPY --from=builder /go/bin/productcatalogservice ./server
COPY products.json .
EXPOSE 3550
ENTRYPOINT ["/productcatalogservice/server"]

