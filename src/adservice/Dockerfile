# adsservice
FROM openjdk:8
RUN apt-get update && apt-get install net-tools telnet
WORKDIR /app
COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN ./gradlew downloadRepos

COPY . .
RUN ./gradlew installDist
EXPOSE 9555
ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]
