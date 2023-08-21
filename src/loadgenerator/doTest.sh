#!/bin/sh
sleep 60 #wait for all microservices to start
sl-python pytest --teststage "Pytest tests"  --labid $SL_LABID --token $SL_TOKEN test_pytest.py
sl-python end --labid $SL_LABID --token $SL_TOKEN
sleep 600