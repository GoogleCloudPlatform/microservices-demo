FROM python:3.9-alpine

RUN apk --no-cache add g++ zeromq-dev libffi-dev file make gcc musl-dev bash curl

WORKDIR /app
COPY . .
RUN pip install -U -r requirements.txt

RUN chmod +x ./loadgen.sh
ENTRYPOINT ./loadgen.sh
