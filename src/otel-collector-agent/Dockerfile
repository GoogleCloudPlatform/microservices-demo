FROM otel/opentelemetry-collector-contrib:0.49.0

ARG NEW_RELIC_API_KEY
ARG OTEL_EXPORTER_OTLP_ENDPOINT

ENV NEW_RELIC_API_KEY=${NEW_RELIC_API_KEY}
ENV OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT}

COPY ./collector.yaml /etc/otel/config.yaml

ENTRYPOINT ["/otelcol-contrib"]
CMD ["/otelcol-contrib", "--config=/etc/otel/config.yaml"]
