#FROM microsoft/dotnet:2.2-sdk-alpine as builder
FROM mcr.microsoft.com/dotnet/core/sdk:3.1-alpine as builder

RUN apk --update add curl tar

WORKDIR /app
COPY . .
RUN dotnet restore && \
    dotnet build && \
    dotnet publish -c release -r linux-musl-x64 -o /cartservice

# cartservice
FROM alpine:3.8

RUN GRPC_HEALTH_PROBE_VERSION=v0.4.7 && \
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
    icu \
    curl \
    openssl

WORKDIR /app
COPY --from=builder /cartservice .
COPY --from=builder /app/start .

# Add the SFx.NET Instrumentation
ARG TRACER_VERSION=0.2.1
RUN mkdir -p /var/log/signalfx
RUN mkdir -p /opt/signalfx
RUN curl -L https://github.com/signalfx/signalfx-dotnet-tracing/releases/download/v${TRACER_VERSION}/signalfx-dotnet-tracing-${TRACER_VERSION}-musl.tar.gz \
  |  tar xzf - -C /opt/signalfx

ENV CORECLR_ENABLE_PROFILING=1
ENV CORECLR_PROFILER={B4C89B0F-9908-4F73-9F59-0D77C5A06874}
ENV CORECLR_PROFILER_PATH=/opt/signalfx/SignalFx.Tracing.ClrProfiler.Native.so
ENV SIGNALFX_DOTNET_TRACER_HOME=/opt/signalfx

ENTRYPOINT ["./cartservice", "start"]