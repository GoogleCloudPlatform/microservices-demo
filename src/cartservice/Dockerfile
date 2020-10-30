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

FROM mcr.microsoft.com/dotnet/core/sdk:3.1-alpine3.12 as builder
WORKDIR /app
COPY . .
RUN dotnet restore && \
    dotnet build && \
    dotnet publish -c release -r linux-musl-x64 -o /cartservice

# cartservice
FROM alpine:3.8

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

# Dependencies for runtime
# busybox-extras => telnet
RUN apk add --no-cache \
    busybox-extras \
    libc6-compat \
    libunwind \
    libuuid \
    libgcc \
    libstdc++ \
    libssl1.0 \
    libintl \
    icu
WORKDIR /app
COPY --from=builder /cartservice .

ARG NEW_RELIC_API_KEY
ARG NEW_RELIC_TRACE_URL
ARG NEW_RELIC_METRIC_URL
ENV NEW_RELIC_API_KEY=${NEW_RELIC_API_KEY}
ENV NEW_RELIC_TRACE_URL=${NEW_RELIC_TRACE_URL}
ENV NEW_RELIC_METRIC_URL=${NEW_RELIC_METRIC_URL}

ENTRYPOINT ["./cartservice", "start"]
