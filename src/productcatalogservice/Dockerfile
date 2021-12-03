# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM golang:1.15-alpine AS builder
RUN apk add --no-cache ca-certificates git
RUN apk add build-base

WORKDIR /src
# restore dependencies
COPY go.mod go.sum ./
RUN go mod download
COPY . .

# Skaffold passes in debug-oriented compiler flags
ARG SKAFFOLD_GO_GCFLAGS
RUN go build -gcflags="${SKAFFOLD_GO_GCFLAGS}" -o /productcatalogservice .

FROM alpine AS release
RUN apk add --no-cache ca-certificates
RUN GRPC_HEALTH_PROBE_VERSION=v0.4.6 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe
WORKDIR /src
COPY --from=builder /productcatalogservice ./server
COPY products.json .

ARG JAEGER_SERVICE_ADDR
ENV JAEGER_SERVICE_ADDR=${JAEGER_SERVICE_ADDR}

ARG OTEL_EXPORTER_OTLP_SPAN_ENDPOINT
ENV OTEL_EXPORTER_OTLP_SPAN_ENDPOINT=${OTEL_EXPORTER_OTLP_SPAN_ENDPOINT}

ARG OTEL_EXPORTER_OTLP_ENDPOINT
ENV OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT}

ARG DISABLE_TRACING
ENV DISABLE_TRACING=${DISABLE_TRACING}

ARG EXTRA_LATENCY
ENV EXTRA_LATENCY=${EXTRA_LATENCY}

ARG PORT
ENV PORT=${PORT}

ARG DISABLE_STATS
ENV DISABLE_STATS=${DISABLE_STATS}
# Definition of this variable is used by 'skaffold debug' to identify a golang binary.
# Default behavior - a failure prints a stack trace for the current goroutine.
# See https://golang.org/pkg/runtime/
ENV GOTRACEBACK=single

EXPOSE 3550
ENTRYPOINT ["/src/server"]

