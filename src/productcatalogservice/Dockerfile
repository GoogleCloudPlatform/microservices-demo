FROM golang:1.10-alpine AS builder
RUN apk add --no-cache ca-certificates git gcc g++ && \
      wget -qO/go/bin/dep https://github.com/golang/dep/releases/download/v0.5.0/dep-linux-amd64 && \
      chmod +x /go/bin/dep

ENV PROJECT github.com/GoogleCloudPlatform/microservices-demo/src/productcatalogservice
WORKDIR /go/src/$PROJECT

# restore dependencies
COPY Gopkg.* ./
RUN dep ensure --vendor-only -v

COPY . .
RUN go build -gcflags=all='-N -l' -o /productcatalogservice .

FROM alpine AS release
RUN apk add --no-cache ca-certificates \
            libc6-compat

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

WORKDIR /productcatalogservice

RUN wget -O go-cloud-debug https://storage.googleapis.com/cloud-debugger/compute-go/go-cloud-debug \
            && chmod 0755 go-cloud-debug

COPY --from=builder /productcatalogservice ./server
COPY products.json source-context.json* ./

EXPOSE 3550
ENTRYPOINT ["./go-cloud-debug", "-sourcecontext=source-context.json", \
            "-appmodule=productcatalogservice", "-appversion=1.0.0" , \
            "--", "/productcatalogservice/server"]

