# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Define a default value so it's not empty if the builder fails to provide it
ARG BUILDPLATFORM=linux/amd64

FROM --platform=$BUILDPLATFORM python:3.15.1-slim@sha256:533b0b2f9b5d46fd097091cf826f27902f1d6c3bca714b6dc74551356aa97a51 AS base

FROM base AS builder

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

# get packages
WORKDIR /shoppingassistantservice

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.14/ /usr/local/lib/python3.14/

# Add the application
COPY . .

# set listen port
ENV PORT="8080"
EXPOSE 8080

ENTRYPOINT ["python", "shoppingassistantservice.py"]
