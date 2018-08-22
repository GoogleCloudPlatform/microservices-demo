# Ad Service

The Ad service provides advertisement based on context keys. If no context keys are provided then it returns random ads.

## Local Build

The Ad service uses gradlew to compile/install/distribute. Gradle wrapper is already part of the source code. To build Ad Service, run
```
    cd src/adservice; ./gradlew installDist
```
It will create executable script src/adservice/build/install/hipstershop/bin/AdService

### Upgrade gradle version
If you need to upgrade the version of gradle then run
```
    cd src/adservice ; ./gradlew wrapper --gradle-version <new-version>
```

## Docker Build

From repository root, run:

```
docker build --file src/adservice/Dockerfile .
```

