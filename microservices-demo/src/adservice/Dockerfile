FROM gradle:ubi-minimal AS build

WORKDIR /app
COPY build.gradle genproto.sh gradlew settings.gradle /app/
COPY gradle /app/gradle
COPY src /app/src

RUN ./gradlew installDist

FROM eclipse-temurin:19.0.2_7-jre-focal@sha256:4f646d9ba7737e089a937d7a40427f8757f366829a03937b37112e2db5264b54 AS jre

WORKDIR /app
COPY --from=build /app/build/install/hipstershop /app/

FROM alpine AS runtime

RUN apk add --no-cache openjdk21-jre-headless

WORKDIR /app
COPY --from=jre /app /app/.

RUN addgroup -g 1000 adservice && \
    adduser -u 1000 -G adservice -s /bin/sh -D adservice && \
    chown -R adservice:adservice /app

USER adservice
EXPOSE 9555
ENTRYPOINT ["bin/AdService"]