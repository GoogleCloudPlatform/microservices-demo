ARG NET_VERSION=6.0
FROM mcr.microsoft.com/dotnet/sdk:${NET_VERSION} as builder

WORKDIR /app
COPY . .
RUN dotnet restore && \
    dotnet build && \
    dotnet publish -c release -r linux-x64 --no-self-contained -o /cartservice

# cartservice
FROM mcr.microsoft.com/dotnet/aspnet:${NET_VERSION}

# Update and fix critical issues on the distribution
RUN apt-get update
RUN apt-get -y dist-upgrade

ARG GRPC_HEALTH_PROBE_VERSION=v0.4.11
ADD https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 /bin/grpc_health_probe
RUN chmod +x /bin/grpc_health_probe

WORKDIR /app
COPY --from=builder /cartservice .
COPY --from=builder /app/start .

# Add the SFx.NET Instrumentation
ARG TRACER_VERSION=0.2.9
ADD https://github.com/signalfx/signalfx-dotnet-tracing/releases/download/v${TRACER_VERSION}/signalfx-dotnet-tracing_${TRACER_VERSION}_amd64.deb ./

RUN mkdir -p /var/log/signalfx
RUN mkdir -p /opt/signalfx
RUN dpkg -i ./signalfx-dotnet-tracing_${TRACER_VERSION}_amd64.deb
RUN rm ./signalfx-dotnet-tracing_${TRACER_VERSION}_amd64.deb

ENV CORECLR_ENABLE_PROFILING=1
ENV CORECLR_PROFILER={B4C89B0F-9908-4F73-9F59-0D77C5A06874}
ENV CORECLR_PROFILER_PATH=/opt/signalfx/SignalFx.Tracing.ClrProfiler.Native.so
ENV SIGNALFX_DOTNET_TRACER_HOME=/opt/signalfx

ENTRYPOINT ["./cartservice", "start"]
