FROM gradle:ubi-minimal AS build

WORKDIR /app
COPY . .

RUN ./gradlew installDist --no-daemon
RUN chmod +x /app/build/install/hipstershop/bin/AdService

FROM eclipse-temurin:21-jre AS runtime

WORKDIR /app
COPY --from=build /app/build/install/hipstershop /app

EXPOSE 9555
ENTRYPOINT ["/app/bin/AdService"]