#!/bin/bash
export CYPRESS_SL_TEST_STAGE="Cypress-Test-Stage"
export MACHINE_DNS="${MACHINE_DNS1}"
export CYPRESS_SL_LAB_ID="${SL_LABID}"
export CYPRESS_SL_TOKEN="${SL_TOKEN}"
npx cypress run --spec "cypress/integration/api.spec.js"
