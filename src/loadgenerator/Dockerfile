FROM python:3-slim as base

FROM base as builder

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        g++

COPY requirements.txt .

RUN pip install --install-option="--prefix=/install" -r requirements.txt

FROM base
COPY --from=builder /install /usr/local

COPY . .
RUN chmod +x ./loadgen.sh
RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        curl
ENTRYPOINT ./loadgen.sh
