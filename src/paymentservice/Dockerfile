# Copyright 2020 Google LLC
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

FROM node:20.5.0-alpine@sha256:11087abe911baf2fd7e34192f4598bf7e438239e9914f5b7ecda5fb5a7b1a2dd as base

FROM base as builder

# Some packages (e.g. @google-cloud/profiler) require additional
# deps for post-install scripts
RUN apk add --update --no-cache \
    python3 \
    make \
    g++

WORKDIR /usr/src/app

#COPY package*.json ./
COPY . .
RUN npm install --only=production
RUN npm i slnodejs
RUN  ./node_modules/.bin/slnodejs config --tokenfile sltoken.txt --appname "paymentservice" --branch "main" --build "0.4"


RUN ./node_modules/.bin/slnodejs scan --tokenfile sltoken.txt --buildsessionidfile buildSessionId --workspacepath "." --scm none --es6Modules --instrumentForBrowsers --enableOpenTelemetry --outputpath "sl_web"

FROM base

WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/buildSessionId .

#RUN ./node_modules/.bin/slnodejs run --tokenfile sltoken.txt --buildsessionidfile buildSessionId --labid integ_master_loadgenerator --workspacepath "." --useinitialcolor true --useslnode2 -- ./server.js

COPY --from=builder /usr/src/app/node_modules ./node_modules

COPY . .
ENV NODE_DEBUG=sl
EXPOSE 50051

CMD  ./node_modules/.bin/slnodejs run --token "${SL_TOKEN}" --buildsessionidfile buildSessionId --labid "${SL_LAB_ID}" --workspacepath . index.js
