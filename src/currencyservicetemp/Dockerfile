FROM golang:1.10-alpine as builder
RUN apk add --no-cache ca-certificates git
WORKDIR /src/microservices-demo/currencyservice
COPY . .
RUN go get -d ./...
RUN go build -o /currencyservice .

FROM alpine as release
RUN apk add --no-cache \
  ca-certificates
COPY --from=builder /currencyservice /currencyservice
EXPOSE 7000
ENTRYPOINT ["/currencyservice"]
