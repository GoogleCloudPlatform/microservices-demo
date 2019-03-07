FROM python:2.7-slim
RUN apt-get update -qqy && \
	apt-get -qqy install wget g++ && \
	rm -rf /var/lib/apt/lists/*
# show python logs as they occur
ENV PYTHONUNBUFFERED=0

# download the grpc health probe
RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

# get packages
WORKDIR /recommendationservice
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Enable/disable Stackdriver Profiler agent
ENV ENABLE_PROFILER 0

# If code is not running in GCP, follow the documentation at
# https://cloud.google.com/profiler/docs/profiling-external
# and set the following environment variables. Credential key of the service
# account should have the following roles:
# Stackdriver Profiler Agent
# Cloud Trace Agent

#ENV GOOGLE_APPLICATION_CREDENTIALS "key.json"
#ENV GCP_PROJECT_ID "Your GCP project ID"

# add files into working directory
COPY . .

# set listen port
ENV PORT "8080"
EXPOSE 8080

ENTRYPOINT ["python", "/recommendationservice/recommendation_server.py"]
