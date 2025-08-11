FROM gradle:ubi-minimal AS build

WORKDIR /app
COPY build.gradle genproto.sh gradlew settings.gradle /app/
COPY gradle /app/gradle
COPY src /app/src

RUN ./gradlew installDist --no-daemon

FROM gcr.io/distroless/java21-debian12 AS runtime

WORKDIR /app
COPY --from=build /app/build/install/hipstershop /app

EXPOSE 9555
ENTRYPOINT ["bin/AdService"]