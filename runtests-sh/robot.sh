#!/bin/bash
 sl-python start --labid ${params.SL_LABID} --token ${params.SL_TOKEN} --teststage "Robot Tests"
robot -xunit integration-tests/robot-tests/api_tests.robot
sl-python uploadreports --reportfile "unit.xml" --labid ${params.SL_LABID} --token ${params.SL_TOKEN}
sl-python end --labid ${params.SL_LABID} --token ${params.SL_TOKEN}
