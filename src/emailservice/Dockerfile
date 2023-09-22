FROM python:3.10-alpine3.18

RUN apk add --no-cache \
        g++ \
        musl-dev \
        libffi-dev

# get packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

# Download the grpc health probe
RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

WORKDIR /email_server

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python", "email_server.py" ]
