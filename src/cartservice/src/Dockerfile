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

# https://mcr.microsoft.com/v2/dotnet/sdk/tags/list
FROM mcr.microsoft.com/dotnet/sdk:7.0.304-alpine3.18@sha256:abc6384a7ab7fe335e772ab3b154711a89407d2cc3aa077145fdcd65a6f40370 as builder
WORKDIR /app
COPY cartservice.csproj .
RUN dotnet restore cartservice.csproj \
    --use-current-runtime
COPY . .
RUN dotnet publish cartservice.csproj \
    -p:PublishSingleFile=true \
    --use-current-runtime \
    --self-contained true \
    -p:PublishTrimmed=True \
    -p:TrimMode=Link \
    -c release \
    -o /cartservice \
    --no-restore

# https://mcr.microsoft.com/v2/dotnet/runtime-deps/tags/list
FROM mcr.microsoft.com/dotnet/runtime-deps:7.0.7-alpine3.18@sha256:fb139645871d653c5cc427961fc1fcec5a84e7a39775fc1346a3de7640d04af5

WORKDIR /app
COPY --from=builder /cartservice .
EXPOSE 7070
ENV DOTNET_EnableDiagnostics=0 \
    ASPNETCORE_URLS=http://*:7070
USER 1000
ENTRYPOINT ["/app/cartservice"]
