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

FROM --platform=$BUILDPLATFORM eclipse-temurin:21.0.5_11-jdk@sha256:a20cfa6afdbf57ff2c4de77ae2d0e3725a6349f1936b5ad7c3d1b06f6d1b840a AS builder

WORKDIR /app

COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN chmod +x gradlew
RUN ./gradlew downloadRepos

COPY . .
RUN chmod +x gradlew
RUN ./gradlew installDist

FROM eclipse-temurin:21.0.5_11-jre-alpine@sha256:4300bfe1e11f3dfc3e3512f39939f9093cf18d0e581d1ab1ccd0512f32fe33f0

# ==> THIS IS THE CORRECT FIX FOR ALPINE LINUX <==
# Install the gRPC health probe to resolve the CrashLoopBackOff error
RUN apk add --no-cache wget && \
    GRPC_HEALTH_PROBE_VERSION=v0.4.24 && \
    ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
      wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 ; \
    elif [ "$ARCH" = "aarch64" ]; then \
      wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-arm64 ; \
    else \
      echo "Unsupported architecture: $ARCH" && exit 1 ; \
    fi && \
    chmod +x /bin/grpc_health_probe


WORKDIR /app
COPY --from=builder /app .

EXPOSE 9555
ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
