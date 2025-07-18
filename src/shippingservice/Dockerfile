# Stage 1: Build the Go application for shippingservice
FROM golang:1.24.4-alpine AS build

# Set working directory inside the container
WORKDIR /app

# Copy go.mod and go.sum (if they exist)
# These files should be present in src/shippingservice/
COPY go.mod go.sum ./
RUN go mod download # Download Go modules (dependencies)

# Copy the rest of the source code
COPY . .

# Build the shippingservice executable
# The service's main entry point is typically in main.go
RUN CGO_ENABLED=0 go build -o /app/shippingservice-server .

# ==> THIS IS THE FIX <==
# Install wget, then download and prepare the gRPC health probe
RUN apk add --no-cache wget && \
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


# Stage 2: Create the final runtime image
FROM alpine:latest AS final
WORKDIR /app

# Copy the compiled executable from the build stage
COPY --from=build /app/shippingservice-server .

# Copy the gRPC health probe from the build stage
COPY --from=build /bin/grpc_health_probe /bin/grpc_health_probe

# Expose the port on which the shippingservice listens (default 50051)
EXPOSE 50051

# Set the entrypoint for the container
ENTRYPOINT ["/app/shippingservice-server"]
