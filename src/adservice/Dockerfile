FROM adoptopenjdk/openjdk11 as builder

WORKDIR /app

COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN chmod +x gradlew
RUN ./gradlew downloadRepos

COPY . .
RUN chmod +x gradlew
RUN ./gradlew --refresh-dependencies installDist

FROM adoptopenjdk/openjdk11

ENV OTEL_SERVICE_NAME=AdService
ENV OTEL_LOGS_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=DELTA

# Download Stackdriver Profiler Java agent
RUN apt-get -y update && apt-get install -qqy \
    wget \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/cprof && \
    wget -q -O- https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent.tar.gz \
    | tar xzv -C /opt/cprof && \
    rm -rf profiler_java_agent.tar.gz

RUN GRPC_HEALTH_PROBE_VERSION=v0.4.11 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

RUN mkdir -p /app/auto-agent && \
    wget -q -O /app/auto-agent/opentelemetry-agent.jar \
    https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v1.13.0/opentelemetry-javaagent.jar

WORKDIR /app
COPY --from=builder /app .

EXPOSE 9555
ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
