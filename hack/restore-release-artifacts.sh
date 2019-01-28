# Copyright 2019 Google LLC
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


# Restores images ./release/kubernetes-manifests/demo.yaml to match ./kubernetes-manifests

#!/usr/bin/env bash
set -euo pipefail

log() { echo "$1" >&2; }
fail() { log "$1"; exit 1; }

manifestfile="./release/kubernetes-manifests/demo.yaml"

# restore release/ manifest images to skaffold default, eg. "adservice"
for dir in ./src/*/    
do
    svcname=$(basename $dir)
    pattern="^[[:blank:]]*image:.*$svcname.*"
    replace="        image: $svcname"
    sed -i '' "s|$pattern|$replace|g" $manifestfile 
done

log "Restored demo.yaml."
