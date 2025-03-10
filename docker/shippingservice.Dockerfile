FROM golang:1.23.1-alpine@sha256:ac67716dd016429be8d4c2c53a248d7bcdf06d34127d3dc451bda6aa5a87bc06 AS build

WORKDIR /src

# restore dependencies and build the binary

COPY src/shippingservice/go.mod src/shippingservice/go.sum ./

RUN go mod download

COPY src/shippingservice .

RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# we use minimal image for production

FROM alpine:latest

WORKDIR /src

COPY --from=build /src/main .

ENV ENABLE_PROFILER false

EXPOSE 50051

CMD [ "./main" ]