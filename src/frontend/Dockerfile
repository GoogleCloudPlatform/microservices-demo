FROM golang:1.10-alpine as builder
RUN apk add --no-cache ca-certificates git
WORKDIR /go/src/frontend

# fetch known dependencies for caching
RUN go get -d github.com/google/uuid \
    github.com/gorilla/mux \
    github.com/pkg/errors \
    google.golang.org/grpc \
    google.golang.org/grpc/codes \
    google.golang.org/grpc/status

# copy go-only part of the build
COPY *.go ./
COPY ./genproto ./genproto
COPY ./money    ./money

# fetch other dependencies might not have listed above (ideally noop)
RUN go get -d ./...
RUN go install .

# ---

FROM alpine as release
RUN apk add --no-cache ca-certificates \
    busybox-extras net-tools bind-tools
WORKDIR /frontend
COPY --from=builder /go/bin/frontend /frontend/server
COPY ./templates ./templates
COPY ./static ./static
EXPOSE 8080
ENTRYPOINT ["/frontend/server"]
