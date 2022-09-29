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

# based on https://github.com/grpc/grpc/issues/21446#issuecomment-807990690
# and https://groups.google.com/a/google.com/g/veneer-firehose/c/gHfckcGZR9U/m/JD1Kz4lvCwAJ
#
# need to build the libgr-pc_csharp_ext explicitly, copy it into /lib on target
FROM alpine:3.14 AS grpc-build
WORKDIR /opt
RUN apk add --update alpine-sdk autoconf libtool linux-headers cmake git && \ 
    git clone -b v1.43.0 https://github.com/grpc/grpc --depth 1 --shallow-submodules && \
    cd grpc && git submodule update --init --depth 1 && \
    mkdir -p cmake/build && cd cmake/build && \
    cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DgRPC_BACKWARDS_COMPATIBILITY_MODE=ON \
      -DgRPC_BUILD_TESTS=OFF \
      ../.. && \
    make grpc_csharp_ext -j4 && \
    mkdir -p /out && cp libgrpc_csharp_ext.* /out


# https://mcr.microsoft.com/v2/dotnet/sdk/tags/list
FROM mcr.microsoft.com/dotnet/sdk:7.0.100-rc.1 as builder
WORKDIR /app
COPY cartservice.csproj .
RUN dotnet restore cartservice.csproj -r linux-musl-x64
COPY . .
RUN dotnet publish cartservice.csproj -p:PublishSingleFile=true -r linux-musl-x64 --self-contained true -p:PublishTrimmed=True -p:TrimMode=Link -c release -o /cartservice --no-restore

# https://mcr.microsoft.com/v2/dotnet/runtime-deps/tags/list
FROM mcr.microsoft.com/dotnet/runtime-deps:7.0.0-rc.1-alpine3.16-amd64
RUN GRPC_HEALTH_PROBE_VERSION=v0.4.12 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe
WORKDIR /app
COPY --from=grpc-build /out/libgrpc_csharp_ext.so /lib/libgrpc_csharp_ext.x64.so
COPY --from=builder /cartservice .
EXPOSE 7070
ENV DOTNET_EnableDiagnostics=0 \
    ASPNETCORE_URLS=http://*:7070
USER 1000
ENTRYPOINT ["/app/cartservice"]
