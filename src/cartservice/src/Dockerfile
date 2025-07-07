# Stage 1: Build the application
# Use the .NET 9.0 SDK image for building
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /app

# Copy the .csproj file and restore dependencies
# This caches dependencies, so they aren't downloaded every time code changes
COPY cartservice.csproj .
RUN dotnet restore

# Copy the rest of the source code (including Program.cs, Startup.cs, cartstore, services folders)
COPY . .

# Publish the application for release
# --no-restore ensures it uses already restored packages
# -o specifies the output directory for the compiled application
RUN dotnet publish -c Release -o /app/publish --no-restore

# Stage 2: Create the final runtime image
# Use the .NET 9.0 ASP.NET runtime image for the final, smaller image
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app

# Copy the published application from the build stage into the final image
COPY --from=build /app/publish .

# Expose the gRPC port (your cartservice will listen on this port)
# The default for gRPC in this application is often 5000
EXPOSE 5000

# Copy the SSL certificate into the container
# This path inside the container (/ssl/DigiCertGlobalRootCA.crt.pem)
# MUST match the CertificateFile path in your AZURE_MYSQL_CONNECTION_STRING.
# The 'COPY' command here assumes your 'ssl' folder is at
# D:\DevOps Projects\microservices-demo\src\ssl
# relative to where you run the 'docker build' command (D:\DevOps Projects\microservices-demo\src\cartservice\src).
COPY ./ssl/DigiCertGlobalRootCA.crt.pem /ssl/DigiCertGlobalRootCA.crt.pem

# Set the entry point for the application when the container starts
ENTRYPOINT ["dotnet", "cartservice.dll"]