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

FROM golang:1.21.6-alpine@sha256:a6a7f1fcf12f5efa9e04b1e75020931a616cd707f14f62ab5262bfbe109aa84a as builder
RUN apk add --no-cache ca-certificates git
RUN apk add build-base
WORKDIR /src

# restore dependencies
COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Skaffold passes in debug-oriented compiler flags
ARG SKAFFOLD_GO_GCFLAGS
RUN go build -gcflags="${SKAFFOLD_GO_GCFLAGS}" -o /checkoutservice .

FROM alpine:3.19.0@sha256:51b67269f354137895d43f3b3d810bfacd3945438e94dc5ac55fdac340352f48
RUN apk add --no-cache ca-certificates

WORKDIR /src
COPY --from=builder /checkoutservice /src/checkoutservice

# Definition of this variable is used by 'skaffold debug' to identify a golang binary.
# Default behavior - a failure prints a stack trace for the current goroutine.
# See https://golang.org/pkg/runtime/
ENV GOTRACEBACK=single

EXPOSE 5050
ENTRYPOINT ["/src/checkoutservice"]
