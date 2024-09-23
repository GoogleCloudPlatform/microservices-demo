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

FROM eclipse-temurin:21@sha256:e538e34d1df871c9b7da571582cdc49538f1eaee1dacbfb317a3e7f54abeebae AS builder

WORKDIR /app

COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN chmod +x gradlew
RUN ./gradlew downloadRepos

COPY . .
RUN chmod +x gradlew
RUN ./gradlew installDist

FROM eclipse-temurin:21.0.4_7-jre-alpine@sha256:8cc1202a100e72f6e91bf05ab274b373a5def789ab6d9e3e293a61236662ac27

# @TODO: https://github.com/GoogleCloudPlatform/microservices-demo/issues/2517
# Download Stackdriver Profiler Java agent
# RUN mkdir -p /opt/cprof && \
#     wget -q -O- https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent_alpine.tar.gz \
#     | tar xzv -C /opt/cprof && \
#     rm -rf profiler_java_agent.tar.gz

WORKDIR /app
COPY --from=builder /app .

EXPOSE 9555
ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
