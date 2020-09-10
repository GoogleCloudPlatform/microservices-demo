FROM microsoft/dotnet:2.1-sdk-alpine as builder

RUN apk --update add curl tar
RUN curl -L https://github.com/signalfx/signalfx-dotnet-tracing/releases/download/v0.1.2/signalfx-dotnet-tracing-0.1.2-musl.tar.gz -o  signalfx-dotnet-tracing-musl.tar.gz
RUN tar -xf signalfx-dotnet-tracing-musl.tar.gz -C /

WORKDIR /app
COPY . .
RUN dotnet restore && \
    dotnet build && \
    dotnet publish -c release -r linux-musl-x64 -o /cartservice

# cartservice
FROM alpine:3.8

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

# Dependencies for runtime
# busybox-extras => telnet
RUN apk add --no-cache \
    busybox-extras \
    libc6-compat \
    libunwind \
    libuuid \
    libgcc \
    libstdc++ \
    libintl \
    icu

WORKDIR /app
COPY --from=builder /cartservice .
COPY --from=builder /app/start .
COPY --from=builder /opt/signalfx-dotnet-tracing/* /opt/signalfx-dotnet-tracing/
ENTRYPOINT ["./start"]