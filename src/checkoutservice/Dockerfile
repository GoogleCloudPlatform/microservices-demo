FROM golang:1.10-alpine as builder
RUN apk add --no-cache ca-certificates git
WORKDIR /src/microservices-demo/catalogservice
COPY . .
RUN go get -d ./...
RUN go build -o /catalogservice .

FROM alpine as release
RUN apk add --no-cache \
  ca-certificates
COPY --from=builder /catalogservice /catalogservice
EXPOSE 5000
ENTRYPOINT /catalogservice
