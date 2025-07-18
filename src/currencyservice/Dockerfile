# Use a stable Node.js image
FROM node:18-alpine AS build

# Install python3, make, g++ for node-gyp native module builds
RUN apk add --no-cache python3 make g++

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# ==> THIS IS THE CORRECT FIX FOR ALPINE LINUX <==
# Install the gRPC health probe to resolve the CrashLoopBackOff error
ARG TARGETARCH
RUN apk add --no-cache wget && \
    GRPC_HEALTH_PROBE_VERSION=v0.4.24 && \
    if [ "$TARGETARCH" = "amd64" ]; then \
      wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 ; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
      wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-arm64 ; \
    else \
      echo "Unsupported architecture: $TARGETARCH" && exit 1 ; \
    fi && \
    chmod +x /bin/grpc_health_probe

# Copy the rest of the application source code
COPY . .

# Expose the port the service listens on
EXPOSE 7000

# Define the command to run the service
ENTRYPOINT ["node", "server.js"]
