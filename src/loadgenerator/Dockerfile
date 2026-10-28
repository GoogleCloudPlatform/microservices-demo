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

# This artifact-only image carries the prebuilt Faker WASM component.
FROM ghcr.io/perfscale/faker:0.1.0@sha256:7c2657d2bd797f9134a67877fdf9df14de410f5e1d200a7a9610409de094f3fd AS faker

# The official Perfscale image already contains the binary and a non-root user.
# No compiler, source checkout, Python runtime, or Locust dependencies are needed.
FROM ghcr.io/perfscale/perfscale:0.28.0@sha256:7853b8f943dfea0aa18bc1cade3c40f7f3c56b76488a258cdd358d1c176181a1

WORKDIR /loadgen

COPY test.yaml config.template.yaml ./
COPY --chmod=0755 run-perfscale.sh ./
COPY --from=faker /faker.wasm ./

ENV FRONTEND_ADDR=http://localhost:8080 \
    USERS=10 \
    RATE=1 \
    DURATION=1h \
    RAMP_DOWN=30s \
    PERFSCALE_BIN=perfscale

USER perfscale
ENTRYPOINT ["/loadgen/run-perfscale.sh"]
