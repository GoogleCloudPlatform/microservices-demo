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

# This script creates a new release by:
# - 1. building/pushing images
# - 2. injecting tags into YAML manifests
# - 3. creating a new git tag
# - 4. pushing the tag/commit to main.

set -euo pipefail
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT=$SCRIPT_DIR/../..
[[ -n "${DEBUG:-}" ]] && set -x

log() { echo "$1" >&2; }
fail() { log "$1"; exit 1; }

TAG="${TAG:?TAG env variable must be specified}"
REPO_PREFIX="${REPO_PREFIX:?REPO_PREFIX env variable must be specified e.g. us-central1-docker.pkg.dev\/google-samples\/microservices-demo}"
PROJECT_ID="${PROJECT_ID:?PROJECT_ID env variable must be specified e.g. google-samples}"

if [[ "$TAG" != v* ]]; then
    fail "\$TAG must start with 'v', e.g. v0.1.0 (got: $TAG)"
fi

# ensure there are no uncommitted changes
if [[ $(git status -s | wc -l) -gt 0 ]]; then
    echo "error: can't have uncommitted changes"
    exit 1
fi

# make sure local source is up to date
git checkout main
git pull

# build and push images
"${SCRIPT_DIR}"/make-docker-images.sh

# update yaml
"${SCRIPT_DIR}"/make-release-artifacts.sh

# build and push images
"${SCRIPT_DIR}"/make-helm-chart.sh

# create git release / push to new branch
git checkout -b "release/${TAG}"
git add "${REPO_ROOT}/release/"
git add "${REPO_ROOT}/kustomize/base/"
git add "${REPO_ROOT}/helm-chart/"
git commit --allow-empty -m "Release $TAG"
log "Pushing k8s manifests to release/${TAG}..."
git tag "$TAG"
git push --set-upstream origin "release/${TAG}"
git push --tags

log "Successfully tagged release $TAG."
