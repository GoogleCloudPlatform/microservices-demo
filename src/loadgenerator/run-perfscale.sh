#!/bin/sh
# Copyright 2026 Google LLC
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

# FRONTEND_ADDR, USERS and RATE are compatible with the Locust entrypoint.
# DURATION and RAMP_DOWN control the length of each Perfscale run.
set -eu

DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_URL="${FRONTEND_ADDR:-http://localhost:8080}"
case "$BASE_URL" in
  http://*|https://*) ;;
  *) BASE_URL="http://$BASE_URL" ;;
esac
BASE_URL="${BASE_URL%/}"
USERS="${USERS:-10}"
RATE="${RATE:-1}"
DURATION="${DURATION:-1h}"
RAMP_DOWN="${RAMP_DOWN:-30s}"
PERFSCALE_BIN="${PERFSCALE_BIN:-perfscale}"

if ! awk -v users="$USERS" -v rate="$RATE" 'BEGIN {
  exit !(users ~ /^[1-9][0-9]*$/ && rate ~ /^[0-9]+([.][0-9]+)?$/ && rate > 0)
}'; then
  echo "USERS must be a positive integer and RATE must be a positive number" >&2
  exit 2
fi

RAMP_UP="$(awk -v users="$USERS" -v rate="$RATE" 'BEGIN { print users / rate }')s"
export BASE_URL

# Streaming the generated config supports containers with a read-only root filesystem.
sed \
  -e "s/__VUS__/$USERS/g" \
  -e "s/__RAMP_UP__/$RAMP_UP/g" \
  -e "s/__DURATION__/$DURATION/g" \
  -e "s/__RAMP_DOWN__/$RAMP_DOWN/g" \
  "$DIR/config.template.yaml" | \
  "$PERFSCALE_BIN" run -f "$DIR/test.yaml" -c /dev/stdin "$@"
