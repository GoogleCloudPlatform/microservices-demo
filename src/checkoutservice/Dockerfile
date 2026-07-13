# Copyright 2024 Google LLC
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

# ---- Build stage: compile protos + Java, assemble the application dist ----
# Uses the official Gradle image so no Gradle wrapper needs to be committed.
FROM gradle:8.14-jdk21 AS builder

WORKDIR /app

# Copy build config first so the dependency-resolution layer is cached.
COPY settings.gradle build.gradle ./
# Copy sources (includes src/main/proto, compiled by the protobuf plugin).
COPY src ./src

# 'installDist' runs generateProto -> compileJava and lays out a runnable
# distribution (bin/ launcher + lib/ jars) under build/install/hipstershop.
RUN gradle --no-daemon installDist

# ---- Runtime stage: slim JRE with just the built distribution ----
FROM eclipse-temurin:21-jre

# Ensure an interactive shell is available for debugging (kubectl exec -- sh/bash).
RUN apt-get update && apt-get install -y --no-install-recommends bash && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/build/install/hipstershop ./

ENV PORT=5050
EXPOSE 5050

# The 'application' plugin generates bin/hipstershop from mainClass.
ENTRYPOINT ["./bin/hipstershop"]
