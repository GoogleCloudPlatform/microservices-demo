FROM golang:1.22-alpine AS builder
RUN apk add --no-cache ca-certificates git

WORKDIR /app
COPY . .
RUN go build -o /go/bin/frontend .

FROM alpine AS release
RUN apk add --no-cache ca-certificates \
    busybox-extras net-tools bind-tools
WORKDIR /frontend
COPY --from=builder /go/bin/frontend /frontend/server
COPY ./templates ./templates
COPY ./static ./static
EXPOSE 8080
ENTRYPOINT ["/frontend/server"]
