FROM golang:1.15-alpine as builder
RUN apk add --no-cache ca-certificates git
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o /go/bin/otel-system .

FROM alpine as release
RUN apk add --no-cache ca-certificates
WORKDIR /otel-system
COPY --from=builder /go/bin/otel-system /otel-system/server

ARG NEW_RELIC_API_KEY
ARG NEW_RELIC_METRIC_URL
ARG OTLP_EXPORTER_ENDPOINT
ENV NEW_RELIC_API_KEY=${NEW_RELIC_API_KEY}
ENV NEW_RELIC_METRIC_URL=${NEW_RELIC_METRIC_URL}
ENV OTLP_EXPORTER_ENDPOINT=${OTLP_EXPORTER_ENDPOINT}

ENTRYPOINT ["/otel-system/server"]
