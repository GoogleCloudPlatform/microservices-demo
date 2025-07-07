# Stage 1: Build the Go application
FROM golang:1.24.4-alpine AS build 

# Updated Go version to match yours

# Set working directory inside the container
WORKDIR /app

# Copy go.mod and go.sum if they exist (for dependency caching)
# If these files are NOT in your src/frontend/ directory, remove these two COPY lines.
COPY go.mod go.sum ./
# RUN go mod download # Uncomment this line if you copied go.mod/go.sum and use Go modules

# Copy the rest of the source code for the frontend service
COPY . .

# Build the frontend service executable
# CGO_ENABLED=0 creates a statically linked executable, good for small Docker images
RUN CGO_ENABLED=0 go build -o /app/frontend-server .


# Stage 2: Create the final runtime image
FROM alpine:latest AS final   
# Using a minimal Alpine base for a smaller final image
WORKDIR /app

# Copy the compiled executable from the build stage
COPY --from=build /app/frontend-server .

# Copy static assets (HTML templates, CSS, JS, images)
# These paths are relative to the frontend service's src directory
COPY templates ./templates/
COPY static ./static/

# Expose the port on which the frontend service listens (default 8080)
EXPOSE 8080

# Set the entrypoint for the container
ENTRYPOINT ["/app/frontend-server"]