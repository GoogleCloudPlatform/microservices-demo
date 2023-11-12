/*
 * Copyright 2018 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

if(process.env.DISABLE_PROFILER) {
  logger.info("Profiler disabled.")
}
else {
  logger.info("Profiler enabled.")
  require('@google-cloud/profiler').start({
    serviceContext: {
      service: 'paymentservice',
      version: '1.0.0'
    }
  });
}


if(process.env.DISABLE_TRACING) {
  logger.info("Tracing disabled.")
}
else {
  logger.info("Tracing enabled.")
  require('@google-cloud/trace-agent').start();

}

if(process.env.DISABLE_DEBUGGER) {
  logger.info("Debugger disabled.")
}
else {
  logger.info("Debugger enabled.")
  require('@google-cloud/debug-agent').start({
    serviceContext: {
      service: 'paymentservice',
      version: 'VERSION'
    }
  });
}


const path = require('path');
const HipsterShopServer = require('./server');

const PORT = process.env['PORT'];
const PROTO_PATH = path.join(__dirname, '/proto/');

const server = new HipsterShopServer(PROTO_PATH, PORT);

const pino = require('pino');
const logger = pino({});

server.listen();
