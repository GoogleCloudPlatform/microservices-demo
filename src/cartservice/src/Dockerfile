# Copyright 2021 Google LLC
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

# https://mcr.microsoft.com/product/dotnet/sdk
FROM mcr.microsoft.com/dotnet/sdk:8.0.203@sha256:9bb0d97c4361cc844f225c144ac2adb2b65fabfef21f95caedcf215d844238fe as builder
WORKDIR /app
COPY cartservice.csproj .
RUN dotnet restore cartservice.csproj \
    -r linux-musl-x64
COPY . .
RUN dotnet publish cartservice.csproj \
    -p:PublishSingleFile=true \
    -r linux-musl-x64 \
    --self-contained true \
    -p:PublishTrimmed=True \
    -p:TrimMode=Full \
    -c release \
    -o /cartservice \
    --no-restore

# https://mcr.microsoft.com/product/dotnet/runtime-deps
FROM mcr.microsoft.com/dotnet/runtime-deps:8.0.3-alpine3.18-amd64@sha256:4714a359cd43936ac1b8eb0a55e032c9929aba255e0f5f70c3365bec023c4b0b

WORKDIR /app
COPY --from=builder /cartservice .
EXPOSE 7070
ENV DOTNET_EnableDiagnostics=0 \
    ASPNETCORE_HTTP_PORTS=7070
USER 1000
ENTRYPOINT ["/app/cartservice"]
