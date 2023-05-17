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

FROM golang:1.20.4-alpine@sha256:0a03b591c358a0bb02e39b93c30e955358dadd18dc507087a3b7f3912c17fe13 AS builder
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

FROM alpine:3.18.0@sha256:02bb6f428431fbc2809c5d1b41eab5a68350194fb508869a33cb1af4444c9b11 AS without-grpc-health-probe-bin
RUN apk add --no-cache ca-certificates

WORKDIR /src
COPY --from=builder /productcatalogservice ./server
COPY products.json .

# Definition of this variable is used by 'skaffold debug' to identify a golang binary.
# Default behavior - a failure prints a stack trace for the current goroutine.
# See https://golang.org/pkg/runtime/
ENV GOTRACEBACK=single

EXPOSE 3550
ENTRYPOINT ["/src/server"]

FROM without-grpc-health-probe-bin
# renovate: datasource=github-releases depName=grpc-ecosystem/grpc-health-probe
ENV GRPC_HEALTH_PROBE_VERSION=v0.4.18
RUN wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe