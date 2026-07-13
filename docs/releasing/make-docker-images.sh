#!/usr/bin/env bash

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

set -euo pipefail
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT=$SCRIPT_DIR/../..

log() { echo "$1" >&2; }

TAG="${TAG:?TAG env variable must be specified}"
REPO_PREFIX="${REPO_PREFIX:?REPO_PREFIX env variable must be specified}"
PROJECT_ID="${PROJECT_ID:?PROJECT_ID env variable must be specified e.g. online-boutique-ci}"

while IFS= read -d $'\0' -r dir; do
    # build image
    svcname="$(basename "${dir}")"
    builddir="${dir}"
    #PR 516 moved cartservice build artifacts one level down to src
    if [ $svcname == "cartservice" ]
    then
        builddir="${dir}/src"
    fi
    image="${REPO_PREFIX}/$svcname:$TAG"
    image_with_sample_public_image_tag="${REPO_PREFIX}/$svcname:sample-public-image-$TAG"
    (
        cd "${builddir}"
        log "Building (and pushing) image on Google Cloud Build: ${image}"
        log "Submitting Cloud Build job..."
        build_id=$(gcloud builds submit --project=${PROJECT_ID} --tag=${image} --async --format="value(id)")
        log "Build submitted with ID: ${build_id}. Waiting for completion..."
        while true; do
            status=$(gcloud builds describe ${build_id} --project=${PROJECT_ID} --format="value(status)")
            log "Current build status: ${status}"
            if [[ "$status" == "SUCCESS" ]]; then
                break
            elif [[ "$status" == "FAILURE" || "$status" == "INTERNAL_ERROR" || "$status" == "TIMEOUT" || "$status" == "CANCELLED" ]]; then
                fail "Cloud Build ${build_id} failed with status: ${status}"
            fi
            sleep 10
        done
        gcloud artifacts docker tags add ${image} ${image_with_sample_public_image_tag}
    )
done < <(find "${REPO_ROOT}/src" -mindepth 1 -maxdepth 1 -type d -print0)

log "Successfully built and pushed all images."
