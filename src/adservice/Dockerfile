# Stage 1: Build
FROM gradle:8-jdk21 AS builder

WORKDIR /app

COPY build.gradle settings.gradle ./
COPY src ./src

RUN gradle installDist --no-daemon -Dprotoc.skip=true

# Stage 2: Run
FROM eclipse-temurin:21-jre

WORKDIR /app

COPY --from=builder /app/build/install/hipstershop .

EXPOSE 9555

ENTRYPOINT ["bin/AdService"]