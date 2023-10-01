#!/bin/bash
cd
npx jest integration-tests/nodejs-tests/Jest/test.js --sl-testStage='Jest tests' --sl-token="${SL_TOKEN}" --sl-labId="${SL_LABID}"
cd ../../..