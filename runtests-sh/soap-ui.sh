#!/bin/bash
#wget https://dl.eviware.com/soapuios/5.7.1/SoapUI-5.7.1-mac-bin.zip
#unzip SoapUI-5.7.1-mac-bin.zip
cp integration-tests/soapUI/test-soapui-project.xml SoapUI-5.7.1/bin
cd SoapUI-5.7.1/bin
echo $SL_TOKEN>sltoken.txt
 # shellcheck disable=SC2016
 echo  '{
                      "executionType": "testsonly",
                      "tokenFile": "./sltoken.txt",
                      "createBuildSessionId": false,
                      "testStage": "soapui framework",
                      "runFunctionalTests": true,
                      "labId": "${SL_LABID}",
                      "proxy": null,
                      "logEnabled": false,
                      "logDestination": "console",
                      "logLevel": "warn",
                      "sealightsJvmParams": {}
                      }' > slmaventests.json

echo $MACHINE_DNS1
sed -i "s#machine_dns#${MACHINE_DNS1}#" test-soapui-project.xml
sed "s#machine_dns#${MACHINE_DNS1}#" test-soapui-project.xml

export SL_JAVA_OPTS="-javaagent:sl-test-listener.jar -Dsl.token=${SL_TOKEN} -Dsl.labId=${SL_LABID} -Dsl.testStage=Soapui-Tests -Dsl.log.enabled=true -Dsl.log.level=debug -Dsl.log.toConsole=true"
sed -i -r 's/(^\\S*java)(.*com.eviware.soapui.tools.SoapUITestCaseRunner)/\\1 \\\$SL_JAVA_OPTS \\2/g' testrunner.sh
sh -x ./testrunner.sh -s "TestSuite 1" "test-soapui-project.xml"
cd ../..
