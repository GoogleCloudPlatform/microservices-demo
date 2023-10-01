#!/bin/bash
cd /integration-tests/cucumber-framework
echo $SL_TOKEN>sltoken.txt

# shellcheck disable=SC2016
echo  '{
        "executionType": "testsonly",
        "tokenFile": "./sltoken.txt",
        "createBuildSessionId": false,
        "testStage": "Cucmber framework java ",
        "runFunctionalTests": true,
        "labId": "${SL_LABID}",
        "proxy": null,
        "logEnabled": false,
        "logDestination": "console",
        "logLevel": "warn",
        "sealightsJvmParams": {}
        }' > slmaventests.json
echo "Adding Sealights to Tests Project POM file..."

java -jar sl-build-scanner.jar -pom -configfile slmaventests.json -workspacepath .
unset MAVEN_CONFIG
mvn clean package
cd ../..





