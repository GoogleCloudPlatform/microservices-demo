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

FROM mcr.microsoft.com/dotnet/sdk:9.0@sha256:7d24e90a392e88eb56093e4eb325ff883ad609382a55d42f17fd557b997022ca AS build
WORKDIR /app
COPY . .
RUN dotnet restore cartservice.csproj
RUN dotnet build "./cartservice.csproj" -c Debug -o /out

FROM build AS publish
RUN dotnet publish cartservice.csproj -c Debug -o /out

# Building final image used in running container
FROM mcr.microsoft.com/dotnet/aspnet:9.0@sha256:372b16214ae67e3626a5b1513ade4a530eae10c172d56ce696163b046565fa46 AS final
# Installing procps on the container to enable debugging of .NET Core
RUN apt-get update \
    && apt-get install -y unzip procps wget
WORKDIR /app
COPY --from=publish /out .
ENV ASPNETCORE_HTTP_PORTS=7070

ENTRYPOINT ["dotnet", "cartservice.dll"]
