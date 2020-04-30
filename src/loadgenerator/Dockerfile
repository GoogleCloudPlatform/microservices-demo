FROM locustio/locust:0.14.6

WORKDIR /app
COPY . .

USER root
RUN chmod +x ./loadgen.sh
RUN apk add bash curl

USER locust
ENTRYPOINT ./loadgen.sh
