FROM otel/opentelemetry-collector-contrib:0.49.0

ARG OTEL_EXPORTER_OTLP_ENDPOINT

ENV OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT}

COPY ./collector.yaml /etc/otel/config.yaml

ENTRYPOINT ["/otelcol-contrib"]
CMD ["--config", "/etc/otel/config.yaml"]
