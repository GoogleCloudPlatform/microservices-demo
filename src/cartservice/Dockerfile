FROM gcr.io/dotnet-debugger/aspnetcore:2.1 as builder
ENV d = 1
WORKDIR /app
COPY . .
RUN dotnet restore && \
    dotnet build && \
    dotnet publish -c debug -o /cartservice

# cartservice
FROM gcr.io/dotnet-debugger/aspnetcore:2.1

# Dependencies for runtime
# busybox-extras => telnet
RUN apt-get install -q -y --no-install-recommends \
    busybox \
    libc6 \
    libunwind-dev \
    libuuid1 \
    libgcc1 \
    icu-devtools \
    musl-dev \
    wget 

RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

WORKDIR /app
COPY --from=builder /cartservice .
COPY ./source-context.json /usr/share/dotnet-debugger/agent

ENV STACKDRIVER_DEBUGGER_MODULE=cartservice
ENV STACKDRIVER_DEBUGGER_VERSION=1.0.0

ENTRYPOINT ["/usr/share/dotnet-debugger/start-debugger.sh", "dotnet", "cartservice.dll", "start"]
