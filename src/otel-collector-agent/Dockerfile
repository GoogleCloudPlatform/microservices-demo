FROM golang:1.17 as builder

ARG OTEL_EXPORTER_OTLP_ENDPOINT
ARG OTEL_RESOURCE_ATTRIBUTES

ENV OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT}
ENV OTEL_RESOURCE_ATTRIBUTES=${OTEL_RESOURCE_ATTRIBUTES}

COPY ./collector.yaml /etc/otel/config.yaml

WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download -x

COPY ./cmd/ ./cmd
COPY ./internal/ ./internal

RUN go build ./cmd/otelcontribcol

RUN cp /build/otelcontribcol /

ENTRYPOINT ["/otelcontribcol"]
CMD ["--config", "/etc/otel/config.yaml"]
