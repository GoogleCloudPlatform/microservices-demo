FROM golang:1.10-alpine as builder
RUN apk add --no-cache ca-certificates git
WORKDIR /go/src/frontend
COPY . .

# download known dependencies
RUN go get -d github.com/google/uuid \
    github.com/gorilla/mux \
    google.golang.org/grpc \
    google.golang.org/grpc/codes \
    google.golang.org/grpc/status

# other dependencies might not have listed above
RUN go get -d ./...
RUN go build -o /frontend .

FROM alpine as release
RUN apk add --no-cache ca-certificates
WORKDIR /frontend
COPY --from=builder /frontend /frontend/server
COPY ./templates ./templates
COPY ./static ./static
EXPOSE 8080
ENTRYPOINT ["/frontend/server"]
