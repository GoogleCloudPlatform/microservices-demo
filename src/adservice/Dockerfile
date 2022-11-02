FROM adoptopenjdk/openjdk8:alpine-slim as base

FROM base as builder

WORKDIR /app

COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN chmod +x gradlew
RUN ./gradlew downloadRepos

COPY . .
RUN chmod +x gradlew
RUN ./gradlew installDist

RUN apk --update add curl

WORKDIR /tmp
RUN curl -L https://github.com/signalfx/splunk-otel-java/releases/download/v1.17.0/splunk-otel-javaagent-all.jar -o splunk-otel-javaagent-all.jar

FROM base

RUN mkdir -p /opt/sfx
COPY --from=builder /tmp/splunk-otel-javaagent-all.jar /opt/sfx/splunk-otel-javaagent-all.jar

RUN GRPC_HEALTH_PROBE_VERSION=v0.3.1 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

WORKDIR /app
COPY --from=builder /app .

EXPOSE 9555
ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
