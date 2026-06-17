# Stage 1: Build the Go binary
FROM golang:1.25-alpine AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o frontend .

# Stage 2: Run the binary
FROM alpine:3.19

WORKDIR /app

COPY --from=builder /app/frontend .
COPY --from=builder /app/templates ./templates
COPY --from=builder /app/static ./static

EXPOSE 8080

ENTRYPOINT ["./frontend"]