FROM eclipse-temurin:19@sha256:f3fbf1ad599d4b5dbdd7ceb55708d10cb9fafb08e094ef91e92aa63b520a232e as builder
#FROM eclipse-temurin:17 as builder
WORKDIR /app


COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN chmod +x gradlew
RUN ./gradlew downloadRepos

COPY . .
RUN chmod +x gradlew
RUN ./gradlew installDist

FROM eclipse-temurin:19.0.1_10-jre-alpine@sha256:fabe27bd9db502d484a11d3f571c2f4ef7bba4a172527084d939935358fb06c4
#FROM eclipse-temurin:17.0.8.1_1-jdk-alpine

RUN apk add --no-cache ca-certificates

# Download Stackdriver Profiler Java agent
WORKDIR /app
RUN mkdir -p /opt/cprof && \
    wget -q -O- https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent_alpine.tar.gz \
    | tar xzv -C /opt/cprof && \
    rm -rf profiler_java_agent.tar.gz

COPY --from=builder /app .

EXPOSE 9555


ENTRYPOINT [ "/app/build/install/hipstershop/bin/AdService" ]