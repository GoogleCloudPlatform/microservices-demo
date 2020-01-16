#!/bin/bash
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e
trap "exit" TERM

if [[ -z "${FRONTEND_ADDR}" ]]; then
    echo >&2 "FRONTEND_ADDR not specified"
    exit 1
fi

set -x

# if one request to the frontend fails, then exit
STATUSCODE=$(curl --silent --output /dev/stderr --write-out "%{http_code}" http://${FRONTEND_ADDR})
if test $STATUSCODE -ne 200; then
    echo "Error: Could not reach frontend - Status code: ${STATUSCODE}"
    exit 1
fi

# else, run loadgen
locust --host="http://${FRONTEND_ADDR}" --no-web -c "${USERS:-10}" 2>&1
