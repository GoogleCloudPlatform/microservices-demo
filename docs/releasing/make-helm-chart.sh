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

# Packages and pushes Online Boutique's Helm chart in public Artifact Registry.

set -euo pipefail
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT=$SCRIPT_DIR/../..

log() { echo "$1" >&2; }

TAG="${TAG:?TAG env variable must be specified}"
HELM_CHART_REPO="us-docker.pkg.dev/online-boutique-ci/charts"

cd ${REPO_ROOT}/helm-chart
gsed -i "s/^appVersion:.*/appVersion: \"${TAG}\"/" Chart.yaml
gsed -i "s/^version:.*/version: ${TAG:1}/" Chart.yaml
helm package .
helm push onlineboutique-${TAG:1}.tgz oci://$HELM_CHART_REPO

rm ./onlineboutique-${TAG:1}.tgz

log "Successfully built and pushed the Helm chart."
