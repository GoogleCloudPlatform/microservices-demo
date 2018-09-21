

# Use the grpc.io provided Python image as the base image
FROM grpc/python:1.0

# download the grpc health probe
RUN GRPC_HEALTH_PROBE_VERSION=v0.1.0-alpha.1 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

# show python logs as they occur
ENV PYTHONUNBUFFERED=0

# install pip for python3
RUN apt-get -qqy update && \
        apt-get -qqy install python3-pip

# get packages
WORKDIR /email_server
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python3", "email_server.py" ]
