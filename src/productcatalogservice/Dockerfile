FROM golang:1.10-alpine as builder
RUN apk add --no-cache \
  ca-certificates \
  git
WORKDIR /src/microservices-demo/productcatalogservice
COPY . .
RUN go get -d ./...
RUN go build -o /productcatalogservice .

FROM alpine as release
RUN apk add --no-cache \
  ca-certificates
COPY --from=builder /productcatalogservice /productcatalogservice
EXPOSE 3550
ENTRYPOINT ["/productcatalogservice"]

