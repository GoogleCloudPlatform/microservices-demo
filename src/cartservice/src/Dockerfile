# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0
 
ARG BUILDPLATFORM=linux/amd64
 
# -------------------------------
# Build stage
# -------------------------------
FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:10.0.100-noble@sha256:c7445f141c04f1a6b454181bd098dcfa606c61ba0bd213d0a702489e5bd4cd71 AS builder
 
ARG TARGETARCH=amd64
 
WORKDIR /src
 
COPY cartservice.csproj .
 
RUN dotnet restore cartservice.csproj -a $TARGETARCH
 
COPY . .
 
# Coverage-friendly publish:
# - Debug build
# - portable PDB
# - no single-file publish
# - no trimming
# - no AOT
# - no ReadyToRun
RUN dotnet publish cartservice.csproj \
    -c Debug \
    -a $TARGETARCH \
    -o /cartservice \
    /p:DebugType=portable \
    /p:DebugSymbols=true \
    /p:PublishSingleFile=false \
    /p:SelfContained=false \
    /p:PublishTrimmed=false \
    /p:PublishAot=false \
    /p:PublishReadyToRun=false
 
# -------------------------------
# Runtime stage
# -------------------------------
# Use aspnet image, not runtime-deps.
# aspnet contains dotnet runtime and /bin/sh, required by our Kubernetes coverage YAML.
FROM mcr.microsoft.com/dotnet/aspnet:10.0.0-noble
 
WORKDIR /app
 
COPY --from=builder /cartservice/ /app/
 
EXPOSE 7070
 
ENV ASPNETCORE_HTTP_PORTS=7070 \
    DOTNET_ReadyToRun=0 \
    COMPlus_ReadyToRun=0
 
USER 1000
 
ENTRYPOINT ["dotnet", "cartservice.dll"]