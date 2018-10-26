FROM debian:stretch as base
ENV d = 1

# gRPC and app deps
RUN apt-get update

RUN apt-get install -q -y --no-install-recommends \
  git cmake curl \
  python-dev python-setuptools python-pip \
  build-essential zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev wget curl \
  llvm libncurses5-dev libncursesw5-dev \
  xz-utils tk-dev libffi-dev \
  libssl-dev musl-dev libgirepository1.0-dev libcairo-dev

# Python
ENV PYENV_SHA256 df9449f69918c716e688d4216eb4398d2cd6d2dcd0f7e6f56d55d19d74cc57cc
RUN curl -L https://github.com/pyenv/pyenv/archive/v1.2.6.tar.gz -o pyenv.tar.gz
RUN echo $PYENV_SHA256 pyenv.tar.gz | sha256sum -c
RUN tar zxvf pyenv.tar.gz
RUN mv pyenv-* pyenv
RUN pyenv/plugins/python-build/install.sh
RUN python-build 3.7.0 /usr/local/
RUN rm /usr/local/bin/python

# get packages
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download the grpc health probe
RUN GRPC_HEALTH_PROBE_VERSION=v0.2.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

WORKDIR /email_server

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python3", "email_server.py" ]
