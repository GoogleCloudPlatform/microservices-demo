# Ad Service

The Ad service provides advertisement based on context keys. If no context keys are provided then it returns random ads.

## Building locally

The Ad service uses gradlew to compile/install/distribute. Gradle wrapper is already part of the source code. To build Ad Service, run:

```
./gradlew installDist
```
It will create executable script src/adservice/build/install/hipstershop/bin/AdService

### Upgrading gradle version
If you need to upgrade the version of gradle then run

```
./gradlew wrapper --gradle-version <new-version>
```

## Building docker image

From `src/adservice/`, run:

```
docker build -t adservice ./
```

## Running docker image

```
docker run \
 -p 9555:9555 \
 -e OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net:4317 \
 -e OTEL_EXPORTER_OTLP_HEADERS="api-key={INSERT_NEW_RELIC_API_KEY}" \
 adservice
```

