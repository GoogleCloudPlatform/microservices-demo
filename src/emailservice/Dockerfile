FROM python:3.7-slim as base

FROM base as builder

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as final
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        wget

# Download the grpc health probe
RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

WORKDIR /email_server

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.7/ /usr/local/lib/python3.7/

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python", "email_server.py" ]
