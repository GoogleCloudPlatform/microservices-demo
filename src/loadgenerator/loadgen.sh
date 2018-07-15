#!/bin/bash
set -e
trap "exit" TERM

if [[ -z "${FRONTEND_ADDR}" ]]; then
    echo >&2 "FRONTEND_ADDR not specified"
    exit 1
fi

set -x
locust --host="http://${FRONTEND_ADDR}" --no-web -c "${USERS:-10}"
