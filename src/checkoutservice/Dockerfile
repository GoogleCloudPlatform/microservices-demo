FROM golang:1.10-alpine as builder
RUN apk add --no-cache ca-certificates git
WORKDIR /go/src/checkoutservice
COPY . .
RUN go get -d ./...
RUN go build -o /checkoutservice .

FROM alpine as release
RUN apk add --no-cache ca-certificates
COPY --from=builder /checkoutservice /checkoutservice
EXPOSE 5050
ENTRYPOINT ["/checkoutservice"]
