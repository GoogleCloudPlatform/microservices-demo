FROM golang:1.10-alpine as builder
RUN apk add --no-cache \
  ca-certificates \
  git
WORKDIR /src/microservices-demo/productcatalogservice
# get known dependencies
RUN go get -d google.golang.org/grpc \
    google.golang.org/grpc/codes \
    google.golang.org/grpc/status \
    go.opencensus.io/plugin/ocgrpc \
    go.opencensus.io/trace \
    go.opencensus.io/exporter/stackdriver

COPY . .
# get remaining dependencies
RUN go get -d ./...
RUN go build -o /productcatalogservice .

FROM alpine as release
RUN apk add --no-cache ca-certificates
COPY --from=builder /productcatalogservice /productcatalogservice
EXPOSE 3550
ENTRYPOINT ["/productcatalogservice"]

