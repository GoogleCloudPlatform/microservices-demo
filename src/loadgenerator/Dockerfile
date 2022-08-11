FROM python:3.9-alpine

RUN apk --no-cache add g++ zeromq-dev libffi-dev file make gcc musl-dev bash curl

WORKDIR /app
COPY . .

# To work around https://github.com/gevent/gevent/issues/1899
RUN pip install gevent==21.1.2 --no-build-isolation

RUN pip install -U -r requirements.txt

RUN chmod +x ./loadgen.sh
ENTRYPOINT ./loadgen.sh
