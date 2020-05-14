FROM golang:1.14-alpine as builder
RUN apk add --no-cache ca-certificates git

ENV PROJECT github.com/signalfx/microservices-demo/src/frontend
WORKDIR /go/src/$PROJECT

COPY . .
ENV GO111MODULE on
RUN go build -o /go/bin/frontend .

FROM alpine as release
RUN apk add --no-cache ca-certificates \
    busybox-extras net-tools bind-tools
WORKDIR /frontend
COPY --from=builder /go/bin/frontend /frontend/server
COPY ./templates ./templates
COPY ./static ./static
EXPOSE 8080
ENTRYPOINT ["/frontend/server"]
