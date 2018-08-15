# cartservice
FROM openjdk:8
RUN apt-get update && apt-get install net-tools telnet
WORKDIR /app
COPY build/install .
EXPOSE 9555
ENTRYPOINT ["/app/hipstershop/bin/AdsService"]
#ENTRYPOINT ["ls /"]

