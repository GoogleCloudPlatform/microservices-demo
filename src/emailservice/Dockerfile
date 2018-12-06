FROM python:3-alpine as base

FROM base as builder

# gRPC and app deps
RUN apk add --update --no-cache \
    gcc \
    linux-headers \
    make \
    musl-dev \
    python-dev \
    g++ \
    # App Deps
    cairo-dev \
    cairo \
    openssl-dev \
    gobject-introspection-dev

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as final

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

# Download the grpc health probe
RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

WORKDIR /email_server

# Grab packages from builder
COPY --from=builder /usr/local/lib/python3.7/ /usr/local/lib/python3.7/

# Need libstdc++ for grpc
RUN apk add --no-cache libstdc++

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python", "email_server.py" ]
