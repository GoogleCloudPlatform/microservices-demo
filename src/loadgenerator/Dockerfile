FROM python:3-alpine as base

FROM base as builder

RUN apk add --update --no-cache \
    gcc \
    linux-headers \
    make \
    musl-dev \
    python-dev \
    g++

COPY requirements.txt .

RUN pip install --install-option="--prefix=/install" -r requirements.txt

FROM base
COPY --from=builder /install /usr/local

COPY . .
ENTRYPOINT ./loadgen.sh
