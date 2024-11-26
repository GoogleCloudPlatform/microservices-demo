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

FROM python:3.13.0-alpine@sha256:6fe2f8718e257d8be95f79e3ad3659183f01b0b28fe1d50f5f6e3c54ebbd8f12 AS base

FROM base AS builder

RUN apk update \
    && apk add --no-cache wget g++ \
    && rm -rf /var/cache/apk/*

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

WORKDIR /email_server

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.13/ /usr/local/lib/python3.13/

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python", "email_server.py" ]
