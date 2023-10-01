#!/bin/bash
cd integration-tests/postman-tests
./node_modules/.bin/slnodejs start --labid ${SL_LABID} --token ${SL_TOKEN} --teststage "postman tests"
npx newman run sealights-excersise.postman_collection.json --env-var machine_dns=$MACHINE_DNS1 -r xunit --reporter-xunit-export './result.xml' --suppress-exit-code
./node_modules/.bin/slnodejs uploadReports --labid ${SL_LABID} --token ${SL_TOKEN} --reportFile './result.xml'
./node_modules/.bin/slnodejs end --labid ${SL_LABID} --token ${SL_TOKEN}
cd ../..
