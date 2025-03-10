FROM golang:1.23.1-alpine@sha256:ac67716dd016429be8d4c2c53a248d7bcdf06d34127d3dc451bda6aa5a87bc06 AS build

WORKDIR /src

COPY src/checkoutservice/go.mod src/checkoutservice/go.sum ./
COPY src/checkoutservice .

RUN go mod download && \
    CGO_ENABLED=0 GOOS=linux go build -o main .

FROM scratch 

WORKDIR /app

COPY --from=build /src/main .

EXPOSE 5050

CMD [ "./main" ]