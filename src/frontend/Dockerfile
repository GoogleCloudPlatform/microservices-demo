# Stage 1: Build the Go application
FROM golang:1.24.4-alpine AS build

# Set working directory inside the container
WORKDIR /app

# Copy go.mod and go.sum for dependency caching
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the source code for the frontend service
COPY . .

# Build the frontend service executable
RUN CGO_ENABLED=0 go build -o /app/frontend-server .


# Stage 2: Create the final runtime image
FROM alpine:latest AS final
WORKDIR /app

# Copy the compiled executable from the build stage
COPY --from=build /app/frontend-server .

# Copy static assets (HTML templates, CSS, JS, images)
COPY templates ./templates/
COPY static ./static/

# Expose the port on which the frontend service listens
EXPOSE 8080

# Set the entrypoint for the container
ENTRYPOINT ["/app/frontend-server"]
