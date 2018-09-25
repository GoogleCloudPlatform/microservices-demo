FROM python:2.7-alpine3.8 as base

FROM base as builder

# gRPC deps
RUN apk add --update --no-cache \
    gcc \
    linux-headers \
    make \
    musl-dev \
    python-dev \
    g++ \
    cairo-dev \
    cairo \
    openssl-dev \ 
    gobject-introspection-dev

ENV GRPC_PYTHON_VERSION 1.15.0

# Install grpcio
RUN python -m pip install --upgrade pip
RUN pip install grpcio==${GRPC_PYTHON_VERSION} grpcio-tools==${GRPC_PYTHON_VERSION}

# get packages
COPY requirements.txt .

RUN pip install -r requirements.txt


FROM base as final

# Download the grpc health probe
RUN GRPC_HEALTH_PROBE_VERSION=v0.1.0-alpha.1 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

# Show python logs as they occur
ENV PYTHONUNBUFFERED=0

WORKDIR /email_server

# Grab packages from builder
COPY --from=builder /usr/local/lib/python2.7/ /usr/local/lib/python2.7/

# Need libstdc++ for grpc
RUN apk add --no-cache libstdc++

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python", "email_server.py" ]