#!/bin/bash
set -e

if [[ -z "${FRONTEND_ADDR}" ]]; then
    echo >&2 "FRONTEND_ADDR not specified"
    exit 1
fi

set -x
# add "timeout 3600" because locust locks up/freezes for some reason
timeout 3600 locust --host="http://${FRONTEND_ADDR}" --no-web -c "${USERS:-10}" -r 10 
