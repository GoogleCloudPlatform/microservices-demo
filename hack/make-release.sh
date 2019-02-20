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
# - 4. pushing the tag/commit to master.

set -euo pipefail
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
[[ -n "${DEBUG:-}" ]] && set -x

log() { echo "$1" >&2; }
fail() { log "$1"; exit 1; }

TAG="${TAG:?TAG env variable must be specified}"
REPO_PREFIX="${REPO_PREFIX:?REPO_PREFIX env variable must be specified e.g. gcr.io\/google-samples\/microservices-demo}"

if [[ "$TAG" != v* ]]; then
    fail "\$TAG must start with 'v', e.g. v0.1.0 (got: $TAG)"
fi

# build and push images
"${SCRIPTDIR}"/make-docker-images.sh

# update yaml
"${SCRIPTDIR}"/make-release-artifacts.sh

# create git release / push to master
git add "${SCRIPTDIR}/../release/"
git commit --allow-empty -m "Release $TAG"
log "Pushing k8s manifests to master..."
git tag "$TAG"
git push --tags
git push origin master

log "Successfully tagged release $TAG."
