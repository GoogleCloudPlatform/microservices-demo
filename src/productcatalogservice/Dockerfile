# Stage 1: Build the Go application for productcatalogservice
FROM golang:1.24.4-alpine AS build 

# Updated Go version

# Set working directory inside the container
WORKDIR /app

# Copy go.mod and go.sum (if they exist)
COPY go.mod go.sum ./
RUN go mod download
RUN go mod verify
RUN go get github.com/go-sql-driver/mysql

# Copy the rest of the source code
COPY . .

# Build the productcatalogservice executable
# RUN CGO_ENABLED=0 go build -o /app/productcatalogservice-server ./server.go
RUN CGO_ENABLED=0 go build -o /app/productcatalogservice-server .



# Stage 2: Create the final runtime image
FROM alpine:latest AS final
WORKDIR /app

# Copy the compiled executable from the build stage
COPY --from=build /app/productcatalogservice-server .

# Copy the products.json data file, which productcatalogservice uses
COPY products.json .

# Expose the port on which the productcatalogservice listens (default 3550)
EXPOSE 3550

# Set the entrypoint for the container
ENTRYPOINT ["/app/productcatalogservice-server"]
