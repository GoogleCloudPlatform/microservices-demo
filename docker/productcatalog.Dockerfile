FROM golang:1.23.1-alpine@sha256:ac67716dd016429be8d4c2c53a248d7bcdf06d34127d3dc451bda6aa5a87bc06 AS build

WORKDIR /src

# restore dependencies and build the binary

COPY src/productcatalogservice/go.mod src/productcatalogservice/go.sum ./

COPY src/productcatalogservice/. .

RUN go mod download && \
 CGO_ENABLED=0 GOOS=linux go build -o main .

# we use minimal image for production
FROM scratch

WORKDIR /src

COPY --from=build /src/main .

COPY src/productcatalogservice/products.json .

ENV GOTRACEBACK=single

EXPOSE 3550

CMD [ "./main" ]