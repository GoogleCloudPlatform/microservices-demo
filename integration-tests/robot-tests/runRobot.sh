pip install robotframework
pip install robotframework-requests
pip install sealights-python-agent

sl-python start --labid ${SL_LAB_ID} --token ${SL_TOKEN} --teststage "Robot Tests" #add token and labid
robot -xunit ./api_tests.robot
sl-python uploadreports --reportfile "unit.xml" --labid ${SL_LAB_ID} --token ${SL_TOKEN} 
sl-python end --labid ${SL_LAB_ID} --token ${SL_TOKEN}
