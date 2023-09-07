FROM python:3.10.8-slim@sha256:49749648f4426b31b20fca55ad854caa55ff59dc604f2f76b57d814e0a47c181 as builder

ARG BUILD_NAME
ARG SEALIGHTS_TOKEN

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        wget g++ git \
    && rm -rf /var/lib/apt/lists/*

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install sealights-python-agent
WORKDIR /emailservice
COPY . .
RUN sl-python config --appname emailservice --branchname main --buildname ${BUILD_NAME} --workspacepath ./ --token ${SEALIGHTS_TOKEN}
RUN export SL_BUILD_SESSION_ID=`cat buildSessionId.txt`
RUN sl-python scan --scm none --token ${SEALIGHTS_TOKEN}

FROM python:3.10.8-slim@sha256:49749648f4426b31b20fca55ad854caa55ff59dc604f2f76b57d814e0a47c181

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
RUN pip install sealights-python-agent

COPY --from=builder /usr/local/lib/python3.10/ /usr/local/lib/python3.10/
WORKDIR /emailservice
COPY . .
COPY --from=builder /emailservice/buildSessionId.txt .
RUN export SL_BUILD_SESSION_ID=`cat buildSessionId.txt`
RUN export SL_DEBUG=true
# Add the application
ENV PORT "8080"
EXPOSE 8080 
CMD sl-python run python email_server.py --labid ${SL_LAB_ID} --token ${SL_TOKEN}
