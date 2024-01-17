FROM golang:1.18 as builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download
COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -v -o loadgen cmd/loadgen/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/loadgen .
ENTRYPOINT ["./loadgen", "-users=${USERS:-10}", "-url=http://${FRONTEND_ADDR}"]

