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

# injects new image/tag into the images in ./release/kubernetes-manifests/demo.yaml 

#!/usr/bin/env bash
set -euo pipefail

log() { echo "$1" >&2; }
fail() { log "$1"; exit 1; }

TAG="${TAG?TAG env variable must be specified}"
REPO_PREFIX="${REPO_PREFIX?REPO_PREFIX env variable must be specified}"


# inject new tag into the relevant k8s manifest
manifestfile="./release/kubernetes-manifests/demo.yaml"

for dir in ./src/*/    
do
    svcname="$(basename $dir)"
    image="$REPO_PREFIX/$svcname:$TAG"

    pattern=".*image:.*$svcname.*"
    replace="        image: $image"
    sed -i '' "s|$pattern|$replace|g" $manifestfile 
done


log "Successfully injected image tag into demo.yaml".
