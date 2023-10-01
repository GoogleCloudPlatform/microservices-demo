#!/bin/bash
sl-python pytest --teststage "Pytest tests"  --labid ${SL_LABID} --token ${SL_TOKEN} integration-tests/python-tests/python-tests.py
sl-python end --labid ${SL_LABID} --token ${SL_TOKEN}
