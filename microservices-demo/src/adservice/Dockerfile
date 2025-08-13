FROM gradle:ubi-minimal AS build

WORKDIR /app
COPY . .

RUN ./gradlew installDist --no-daemon
RUN jdeps --ignore-missing-deps -q  \
    --recursive  \  
    --multi-release 17  \
    --print-module-deps  \
    /app/build/install/hipstershop/lib/*.jar > modules.txt

RUN jlink \
    --add-modules $(cat modules.txt) \
    --strip-debug \
    --no-man-pages \
    --no-header-files \
    --compress 2 \
    --output /min-app-jre

FROM debian:bookworm-slim@sha256:b1a741487078b369e78119849663d7f1a5341ef2768798f7b7406c4240f86aef AS runtime

WORKDIR /app

COPY --from=build /min-app-jre /app/jre
COPY --from=build /app/build/install/hipstershop /app

ENV JAVA_HOME=/app/jre
ENV PATH="${JAVA_HOME}/bin:${PATH}"

EXPOSE 9555
ENTRYPOINT ["/app/bin/AdService"]