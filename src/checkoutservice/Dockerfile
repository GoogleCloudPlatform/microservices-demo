FROM golang:1.10-alpine as builder
RUN apk add --no-cache ca-certificates git
WORKDIR /go/src/checkoutservice

# get known dependencies
RUN go get -d github.com/google/uuid \
    google.golang.org/grpc \
    google.golang.org/grpc/codes \
    google.golang.org/grpc/status \
    go.opencensus.io/plugin/ocgrpc \
    go.opencensus.io/exporter/stackdriver \
	go.opencensus.io/trace
COPY . .
# get remaining dependencies
RUN go get -d ./...
RUN go build -o /checkoutservice .

FROM alpine as release
RUN apk add --no-cache ca-certificates
COPY --from=builder /checkoutservice /checkoutservice
EXPOSE 5050
ENTRYPOINT ["/checkoutservice"]
