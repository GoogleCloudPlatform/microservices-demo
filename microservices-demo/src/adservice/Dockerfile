FROM gradle:ubi-minimal AS build

WORKDIR /app
COPY build.gradle genproto.sh gradlew settings.gradle /app/
COPY gradle /app/gradle
COPY src /app/src

RUN ./gradlew installDist --no-daemon

FROM alpine AS runtime

RUN apk add --no-cache openjdk21-jre-headless

WORKDIR /app
COPY --from=build /app/build/install/hipstershop /app/

RUN addgroup -g 1000 adservice && \
    adduser -u 1000 -G adservice -s /bin/sh -D adservice && \
    chown -R adservice:adservice /app

USER adservice
EXPOSE 9555
ENTRYPOINT ["bin/AdService"]