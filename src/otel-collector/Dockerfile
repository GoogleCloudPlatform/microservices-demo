FROM alpine:latest AS build

ARG NEW_RELIC_API_KEY
ARG NEW_RELIC_TRACE_URL
ARG NEW_RELIC_METRIC_URL

ENV NEW_RELIC_API_KEY=${NEW_RELIC_API_KEY}
ENV NEW_RELIC_TRACE_URL=${NEW_RELIC_TRACE_URL}
ENV NEW_RELIC_METRIC_URL=${NEW_RELIC_METRIC_URL}

COPY ./collector.yaml /etc/otel/config.yaml
RUN sed -i "s/NEW_RELIC_API_KEY/${NEW_RELIC_API_KEY}/g" /etc/otel/config.yaml
RUN sed -i "s#NEW_RELIC_TRACE_URL#${NEW_RELIC_TRACE_URL}#g" /etc/otel/config.yaml
RUN sed -i "s#NEW_RELIC_METRIC_URL#${NEW_RELIC_METRIC_URL}#g" /etc/otel/config.yaml

FROM otel/opentelemetry-collector-contrib:0.16.0

COPY --from=build /etc/otel/config.yaml /etc/otel/config.yaml

ENTRYPOINT ["/otelcontribcol"]
CMD ["--config", "/etc/otel/config.yaml"]
EXPOSE 55680 55679 9411 14250 14268 13133 4317
