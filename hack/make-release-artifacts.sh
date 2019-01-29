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

# injects new image/tag into the images in ./release/kubernetes-manifests/demo.yaml 

set -euo pipefail
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

log() { echo "$1" >&2; }

TAG="${TAG?TAG env variable must be specified}"
REPO_PREFIX="${REPO_PREFIX?REPO_PREFIX env variable must be specified}"
out_file="${SCRIPTDIR}/../release/kubernetes-manifests/demo.yaml"

read_manifests() {
    local src_manifest_dir
    src_manifest_dir="${SCRIPTDIR}/../kubernetes-manifests"

    while IFS= read -d $'\0' -r file; do
        cat "${file}"
        echo "---"
    done < <(find "${src_manifest_dir}" -name '*.yaml' -type f -print0)
}

# read and merge all manifests
out_manifest="$(read_manifests)"

# replace "image" repo, tag for each service
for dir in ./src/*/
do
    svcname="$(basename "${dir}")"
    image="$REPO_PREFIX/$svcname:$TAG"

    pattern="^(\s*)image:\s.*$svcname(.*)(\s*)"
    replace="\1image: $image\3"
    out_manifest="$(gsed -r "s|$pattern|$replace|g" <(echo "${out_manifest}") )"
done

rm -rf -- "${out_file}"
mkdir -p "$(dirname "${out_file}")"
echo "${out_manifest}" > "${out_file}"

log "Successfully saved merged manifests to ${out_file}."
