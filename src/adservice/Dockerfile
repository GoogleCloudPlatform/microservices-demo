FROM eclipse-temurin:19@sha256:f3fbf1ad599d4b5dbdd7ceb55708d10cb9fafb08e094ef91e92aa63b520a232e as builder

WORKDIR /app

COPY ["build.gradle", "gradlew", "./"]
COPY gradle gradle
RUN chmod +x gradlew
RUN ./gradlew downloadRepos

COPY . .
RUN chmod +x gradlew
RUN ./gradlew installDist

FROM eclipse-temurin:17.0.8.1_1-jre-alpine@sha256:83c4dd3e5481af358343dfffc74934bffc394b1a959bb143a0aafc1e88d4a202

RUN apk add --no-cache ca-certificates

# Download Stackdriver Profiler Java agent
WORKDIR /app
RUN mkdir -p /opt/cprof && \
    wget -q -O- https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent_alpine.tar.gz \
    | tar xzv -C /opt/cprof && \
    rm -rf profiler_java_agent.tar.gz
RUN wget -nv https://agents.sealights.co/sl-cd-agent/sl-cd-agent-latest.zip && \
        unzip -oq sl-cd-agent-latest.zip

COPY --from=builder /app .

EXPOSE 9555
CMD export JAVA_TOOL_OPTIONS="-javaagent:/app/sl-cd-agent.jar -Dsl.branchName=main  -Dsl.token=${SL_TOKEN} -Dsl.appName=adservice -Dsl.buildName=0.1.5.4 -Dsl.tags=script,container -Dsl.labId=${SL_LAB_ID} -Dsl.includes=*hipstershop* -Dsl.workspace=./" && /app/build/install/hipstershop/bin/AdService