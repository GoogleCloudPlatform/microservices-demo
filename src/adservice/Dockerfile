FROM adoptopenjdk/openjdk11 as builder

WORKDIR /app

COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN chmod +x gradlew
RUN ./gradlew downloadRepos

COPY . .
RUN chmod +x gradlew
RUN ./gradlew --refresh-dependencies installDist copyExporters && mkdir -p auto-agent && mv build/exporters/* ./auto-agent/

FROM adoptopenjdk/openjdk11

ARG NEW_RELIC_API_KEY
ARG NEW_RELIC_TRACE_URL
ARG NEW_RELIC_METRIC_URL

ARG USE_ZIPKIN_EXPORTER=false
ENV USE_ZIPKIN_EXPORTER=${USE_ZIPKIN_EXPORTER}

## These 4 are used by the auto-instrumentation configuration:
ENV OTEL_EXPORTER_NEWRELIC_API_KEY=${NEW_RELIC_API_KEY}
ENV OTEL_EXPORTER_NEWRELIC_TRACE_URI_OVERRIDE=${NEW_RELIC_TRACE_URL}
ENV OTEL_EXPORTER_NEWRELIC_METRIC_URI_OVERRIDE=${NEW_RELIC_METRIC_URL}
## TODO: make these env vars injectable somehow
ENV OTEL_EXPORTER_JAR=auto-agent/opentelemetry-exporters-newrelic-auto-0.8.1.jar

# Download Stackdriver Profiler Java agent
RUN apt-get -y update && apt-get install -qqy \
    wget \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/cprof && \
    wget -q -O- https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent.tar.gz \
    | tar xzv -C /opt/cprof && \
    rm -rf profiler_java_agent.tar.gz

RUN GRPC_HEALTH_PROBE_VERSION=v0.3.5 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

RUN mkdir -p /app/auto-agent && \
    wget -q -O /app/auto-agent/opentelemetry-agent.jar \
    https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v0.8.0/opentelemetry-javaagent-all.jar
#    https://oss.jfrog.org/oss-snapshot-local/io/opentelemetry/instrumentation/auto/opentelemetry-javaagent/0.8.0-SNAPSHOT/opentelemetry-javaagent-0.8.0-20200812.231614-27-all.jar

WORKDIR /app
COPY --from=builder /app .

EXPOSE 9555
ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
