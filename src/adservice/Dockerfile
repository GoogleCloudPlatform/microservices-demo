FROM openjdk:8
RUN GRPC_HEALTH_PROBE_VERSION=v0.1.0-alpha.1 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe
WORKDIR /app

# Next three steps are for caching dependency downloads
# to improve subsequent docker build.
COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN ./gradlew downloadRepos

COPY . .
RUN ./gradlew installDist
EXPOSE 9555
ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
