FROM golang:1.18.4-alpine AS builder
RUN apk add --no-cache ca-certificates git
RUN apk add build-base

WORKDIR /build

# restore dependencies
COPY go.mod go.sum ./
RUN go mod download
COPY . .

# Skaffold passes in debug-oriented compiler flags
ARG SKAFFOLD_GO_GCFLAGS
RUN go build -gcflags="${SKAFFOLD_GO_GCFLAGS}" -o cartservice .


FROM alpine AS release
RUN apk add --no-cache ca-certificates
RUN GRPC_HEALTH_PROBE_VERSION=v0.4.11 && \
  wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
  chmod +x /bin/grpc_health_probe

RUN apk update && apk add procps bind-tools net-tools curl

COPY --from=builder /build/cartservice /usr/local/bin/cartservice
# Definition of this variable is used by 'skaffold debug' to identify a golang binary.
# Default behavior - a failure prints a stack trace for the current goroutine.
# See https://golang.org/pkg/runtime/
ENV GOTRACEBACK=single
ENV DISABLE_STATS="1"
ENV JAEGER_SERVICE_ADDR="1"
ENV DISABLE_TRACING="1"
ENV DISABLE_PROFILER="1"

EXPOSE 3550 50000 60000

ENTRYPOINT ["/usr/local/bin/cartservice"]
