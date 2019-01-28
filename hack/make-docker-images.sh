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

# Builds and pushes docker image for each demo microservice. 

#!/usr/bin/env bash
set -euo pipefail

log() { echo "$1" >&2; }
fail() { log "$1"; exit 1; }

TAG="${TAG?TAG env variable must be specified}"
REPO_PREFIX="${REPO_PREFIX?REPO_PREFIX env variable must be specified}"


for dir in ./src/*/    
do
    # build image  
    svcname="$(basename $dir)"
    image="$REPO_PREFIX/$svcname:$TAG"
    echo "Building and pushing $image..." 
    docker build -t $image -f $dir/Dockerfile $dir 

    # push image 
    docker push $image 
done

log "Successfully built and pushed images."
