FROM golang:1.23.1-alpine@sha256:ac67716dd016429be8d4c2c53a248d7bcdf06d34127d3dc451bda6aa5a87bc06 AS builder
WORKDIR /src

# restore dependencies
COPY src/frontend/go.mod src/frontend/go.sum ./
RUN go mod download
COPY src/frontend .

# Skaffold passes in debug-oriented compiler flags
ARG SKAFFOLD_GO_GCFLAGS
RUN CGO_ENABLED=0 GOOS=linux go build -gcflags="${SKAFFOLD_GO_GCFLAGS}" -o /go/bin/frontend .

FROM scratch
WORKDIR /src
COPY --from=builder /go/bin/frontend /src/server
COPY src/frontend/templates ./templates
COPY src/frontend/static ./static

ENV GOTRACEBACK=single

EXPOSE 8080
ENTRYPOINT ["/src/server"]