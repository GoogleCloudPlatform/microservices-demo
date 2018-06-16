FROM golang:1.10.3-alpine3.7 as deps

RUN apk add --no-cache \
  ca-certificates \
  curl \
  git \
  gcc \
  libffi-dev \
  make \
  musl-dev \
  protobuf \
  tar

ENV PATH=$PATH:$GOPATH/bin
RUN go get -u google.golang.org/grpc && \
  go get github.com/golang/protobuf/protoc-gen-go

FROM deps as builder
WORKDIR $GOPATH/src/microservices-demo/shipping
COPY src/shippingservice $GOPATH/src/microservices-demo/shipping
COPY pb/demo.proto $GOPATH/src/microservices-demo/pb/demo.proto

RUN protoc -I ../pb/ ../pb/demo.proto --go_out=plugins=grpc:../pb
RUN go build -o /shipping/shipit

FROM golang:1.10.3-alpine3.7 as release
COPY --from=builder /shipping/shipit /shipit
ENV APP_PORT=50051

# @TODO add light init system.
ENTRYPOINT /shipit
