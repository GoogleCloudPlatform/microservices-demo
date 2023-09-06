FROM eclipse-temurin:17 as builder


WORKDIR /app

COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN chmod +x gradlew
RUN ./gradlew downloadRepos

COPY . .
RUN chmod +x gradlew
RUN ./gradlew installDist

# FROM eclipse-temurin:19.0.1_10-jre-alpine@sha256:a75ea64f676041562cd7d3a54a9764bbfb357b2bf1bebf46e2af73e62d32e36c
FROM eclipse-temurin:17.0.8.1_1-jdk-alpine

RUN apk add --no-cache ca-certificates

# Download Stackdriver Profiler Java agent
WORKDIR /app
RUN mkdir -p /opt/cprof && \
    wget -q -O- https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent_alpine.tar.gz \
    | tar xzv -C /opt/cprof && \
    rm -rf profiler_java_agent.tar.gz

COPY --from=builder /app .

EXPOSE 9555


ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]