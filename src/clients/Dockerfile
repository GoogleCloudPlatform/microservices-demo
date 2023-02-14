FROM golang:1.19.5-alpine

RUN apk add -q --update --progress --no-cache \
  curl        \
  python3     \
  python3-dev
WORKDIR /client

ADD . .

ENV PYTHONUNBUFFERED=1
RUN ln -sf python3 /usr/bin/python \
    && python -m ensurepip \
    && pip3 install --no-cache --upgrade pip \
    pip install -r requirements.txt

CMD ["sleep", "3600"]
