#!/bin/bash
echo $SL_TOKEN>sltoken.txt
# shellcheck disable=SC2016
echo  '{
  "executionType": "testsonly",
  "tokenFile": "./sltoken.txt",
  "createBuildSessionId": false,
  "testStage": "Junit support testNG ",
  "runFunctionalTests": true,
  "labId": "${SL_LABID}",
  "proxy": null,
  "logEnabled": false,
  "logDestination": "console",
  "logLevel": "warn",
  "sealightsJvmParams": {}
  }' > slmaventests.json
echo "Adding Sealights to Tests Project POM file..."
java -jar /sealights/sl-build-scanner.jar -pom -configfile slmaventests.json -workspacepath .

cd integration-tests/support-testNG
mvn test
cd ../..
