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

# Stage 2: Create the final runtime image
FROM alpine:latest AS final
WORKDIR /app

# Copy the compiled executable from the build stage
COPY --from=build /app/shippingservice-server .

# Expose the port on which the shippingservice listens (default 50051)
EXPOSE 50051

# Set the entrypoint for the container
ENTRYPOINT ["/app/shippingservice-server"]