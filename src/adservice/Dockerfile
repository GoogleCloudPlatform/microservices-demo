FROM openjdk:8-alpine as base

FROM base as builder

WORKDIR /app

# This is because the protoc-gen-grpc-java library 
# is a glibc compiled binary and alpine is
# based on musl-libc
RUN  apk add --no-cache --allow-untrusted \
    -X https://apkproxy.herokuapp.com/sgerrand/alpine-pkg-glibc \
    glibc \
    glibc-bin

# Next three steps are for caching dependency downloads
# to improve subsequent docker build.
COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN ./gradlew downloadRepos

COPY . .
RUN ./gradlew installDist

FROM base

RUN GRPC_HEALTH_PROBE_VERSION=v0.1.0-alpha.1 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

WORKDIR /app
COPY --from=builder /app .

EXPOSE 9555
ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
