FROM golang:1.15-alpine as builder

ENV PROJECT github.com/GoogleCloudPlatform/microservices-demo/src/frontend
WORKDIR /go/src/$PROJECT

# restore dependencies
COPY . .
RUN go install .

FROM alpine as release
RUN apk add --no-cache ca-certificates \
    busybox-extras net-tools bind-tools
WORKDIR /frontend
COPY --from=builder /go/bin/frontend /frontend/server
COPY ./templates ./templates
COPY ./static ./static
EXPOSE 8080

ARG NEW_RELIC_API_KEY
ARG NEW_RELIC_TRACE_URL
ARG NEW_RELIC_METRIC_URL
ARG USE_ZIPKIN_EXPORTER=false
ENV NEW_RELIC_API_KEY=${NEW_RELIC_API_KEY}
ENV NEW_RELIC_TRACE_URL=${NEW_RELIC_TRACE_URL}
ENV NEW_RELIC_METRIC_URL=${NEW_RELIC_METRIC_URL}
ENV USE_ZIPKIN_EXPORTER=${USE_ZIPKIN_EXPORTER}

ENTRYPOINT ["/frontend/server"]
