#!/bin/bash
cd integration-tests/nodejs-tests/mocha/
./node_modules/.bin/slnodejs mocha --token "${SL_TOKEN}" --labid "${params.SL_LABID}" --teststage "Mocha tests"  --useslnode2 -- ./test/test.js --recursive --no-timeouts
cd ../../..
