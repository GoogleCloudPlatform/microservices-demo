# Stage 1: Build the application
# Use the .NET 8.0 SDK (LTS version) for better stability in multi-arch builds
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

# Copy the .csproj file and restore dependencies
COPY cartservice.csproj .
RUN dotnet restore

# Copy the rest of the source code
COPY . .

# Publish the application for release
# --no-restore ensures it uses already restored packages
RUN dotnet publish -c Release -o /app/publish --no-restore

# Stage 2: Create the final runtime image
# Use the .NET 8.0 ASP.NET runtime (LTS version)
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final

# ==> THIS IS THE FIX <==
# Install the gRPC health probe to resolve the CrashLoopBackOff error
RUN apt-get update && apt-get install -y wget && \
    GRPC_HEALTH_PROBE_VERSION=v0.4.24 && \
    ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
      wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 ; \
    elif [ "$ARCH" = "aarch64" ]; then \
      wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-arm64 ; \
    else \
      echo "Unsupported architecture: $ARCH" && exit 1 ; \
    fi && \
    chmod +x /bin/grpc_health_probe

WORKDIR /app

# Copy the published application from the build stage
COPY --from=build /app/publish .

# Copy the SSL certificate into the container
COPY ./ssl/DigiCertGlobalRootCA.crt.pem /ssl/DigiCertGlobalRootCA.crt.pem

# Set the entry point for the application
ENTRYPOINT ["dotnet", "cartservice.dll"]
