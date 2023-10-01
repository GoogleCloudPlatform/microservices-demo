#!/bin/bash

echo $SL_TOKEN>sltoken.txt
# shellcheck disable=SC2016
 echo  '{
      "executionType": "testsonly",
      "tokenFile": "./sltoken.txt",
      "createBuildSessionId": false,
      "testStage": "Junit without testNG",
      "runFunctionalTests": true,
      "labId": "${SL_LABID}",
      "proxy": null,
      "logEnabled": false,
      "logDestination": "console",
      "logLevel": "warn",
      "sealightsJvmParams": {}
      }' > slmaventests.json
java -jar sl-build-scanner.jar -pom -configfile slmaventests.json -workspacepath .
# shellcheck disable=SC2164
cd integration-tests/java-tests
mvn clean package
cd ../..
