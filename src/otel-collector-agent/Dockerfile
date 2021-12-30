FROM otel/opentelemetry-collector-contrib:0.40.0

ARG OTEL_EXPORTER_OTLP_ENDPOINT
ARG OTEL_RESOURCE_ATTRIBUTES

ENV OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT}
ENV OTEL_RESOURCE_ATTRIBUTES=${OTEL_RESOURCE_ATTRIBUTES}

COPY ./collector.yaml /etc/otel/config.yaml

ENTRYPOINT ["/otelcontribcol"]
CMD ["--config", "/etc/otel/config.yaml"]
