#!/bin/sh

# Copyright 2018 Google LLC
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


# This script generates code context for the cloud debugger agents
# and populate it to the root directory of each service module.
# This step is necessary if you want to try Cloud Debugger. Otherwise,
# you can simply ignore it.

gcloud debug source gen-repo-info-file
for MODULE in $(find ./src -maxdepth 1 -mindepth 1 -type d); do
   cp source-context.json "$MODULE"
done