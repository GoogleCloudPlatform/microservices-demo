ARG NET_VERSION=7.0
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

# Add the Splunk Distribution of OpenTelemetry .NET
RUN apt-get update && \
    apt-get install -y \
            curl \
            unzip

ARG SPLUNK_OTEL_VERSION=1.0.0-rc.3
ENV OTEL_DOTNET_AUTO_HOME=/.splunk-otel-dotnet
ADD https://github.com/signalfx/splunk-otel-dotnet/releases/download/v${SPLUNK_OTEL_VERSION}/splunk-otel-dotnet-install.sh ./
RUN chmod +x ./splunk-otel-dotnet-install.sh && \
    ./splunk-otel-dotnet-install.sh && \
    rm ./splunk-otel-dotnet-install.sh

ENV CORECLR_ENABLE_PROFILING=1
ENV CORECLR_PROFILER={918728DD-259F-4A6A-AC2B-B85E1B658318}
ENV CORECLR_PROFILER_PATH=/.splunk-otel-dotnet/linux-x64/OpenTelemetry.AutoInstrumentation.Native.so
ENV DOTNET_ADDITIONAL_DEPS=/.splunk-otel-dotnet/AdditionalDeps
ENV DOTNET_SHARED_STORE=/.splunk-otel-dotnet/store
ENV DOTNET_STARTUP_HOOKS=/.splunk-otel-dotnet/net/OpenTelemetry.AutoInstrumentation.StartupHook.dll
ENV OTEL_DOTNET_AUTO_PLUGINS="Splunk.OpenTelemetry.AutoInstrumentation.Plugin, Splunk.OpenTelemetry.AutoInstrumentation"

ENTRYPOINT ["./cartservice", "start"]
