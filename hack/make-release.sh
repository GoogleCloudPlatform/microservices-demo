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

set -euxo pipefail

# set default repo
REPO_PREFIX="${REPO_PREFIX:-gcr.io/google-samples/microservices-demo}"

# move to repo root
SCRIPT_DIR=$(dirname $(realpath -s $0))
REPO_ROOT=$SCRIPT_DIR/..
cd $REPO_ROOT

# validate version number (format: v0.0.0)
if [[ ! "${NEW_VERSION}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "${NEW_VERSION} argument must conform to regex string:  ^v[0-9]+\.[0-9]+\.[0-9]+$ "
    echo "ex. v1.0.1"
    exit 1
fi

# ensure there are no uncommitted changes
if [[ $(git status -s | wc -l) -gt 0 ]]; then
    echo "error: can't have uncommitted changes"
    exit 1
fi

# ensure that gcloud is in the PATH
if ! command -v gcloud &> /dev/null
then
    echo "gcloud could not be found"
    exit 1
fi

# replace kubernetes-manifests/ contents 
rm -rf "${REPO_ROOT}/kubernetes-manifests"
mkdir "${REPO_ROOT}/kubernetes-manifests"
cp -a "${REPO_ROOT}/dev-kubernetes-manifests/." "${REPO_ROOT}/kubernetes-manifests/"

# update version in manifests
find "${REPO_ROOT}/kubernetes-manifests" -name '*.yaml' -exec sed -i -e "s'image: \(.*\)'image: ${REPO_PREFIX}\/\1:${NEW_VERSION}'g" {} \;

# push release PR
git checkout -b "release/${NEW_VERSION}"
git add "${REPO_ROOT}/kubernetes-manifests/*.yaml"
git commit -m "release/${NEW_VERSION}"

# add tag
git tag "${NEW_VERSION}"

# build and push release images
skaffold config set local-cluster false
skaffold build --default-repo="${REPO_PREFIX}" --tag="${NEW_VERSION}"
skaffold config unset local-cluster

# push to repo
git push --set-upstream origin "release/${NEW_VERSION}"
git push --tags