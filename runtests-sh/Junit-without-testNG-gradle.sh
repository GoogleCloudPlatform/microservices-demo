#!/bin/bash
echo $SL_TOKEN>sltoken.txt
 # shellcheck disable=SC2016
 echo  '{
        "executionType": "testsonly",
        "tokenFile": "./sltoken.txt",
        "createBuildSessionId": false,
        "testStage": "Junit without testNG-gradle",
        "runFunctionalTests": true,
        "labId": "${SL_LABID}",
        "proxy": null,
        "logEnabled": false,
        "logDestination": "console",
        "logLevel": "warn",
        "sealightsJvmParams": {}
        }' > slgradletests.json
java -jar /sealights/sl-build-scanner.jar -gradle -configfile slgradletests.json -workspacepath ./microservices-demo/integration-tests/java-tests-gradle
./microservices-demo/integration-tests/java-tests-gradle/gradlew test

