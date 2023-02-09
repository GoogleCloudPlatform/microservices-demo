/*
 * Copyright 2022 Skyramp, Inc.
 *
 *	Licensed under the Apache License, Version 2.0 (the "License");
 *	you may not use this file except in compliance with the License.
 *	You may obtain a copy of the License at
 *
 *	http://www.apache.org/licenses/LICENSE-2.0
 *
 *	Unless required by applicable law or agreed to in writing, software
 *	distributed under the License is distributed on an "AS IS" BASIS,
 *	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *	See the License for the specific language governing permissions and
 *	limitations under the License.
 */
process.on('SIGTERM', cleanup);
process.on('SIGINT', cleanup);


const { Worker } = require('worker_threads')

process.env['REST_PORT'] = 50000;
process.env['THRIFT_PORT'] = 60000;
process.env['DISABLE_PROFILER'] = "1";
process.env['DISABLE_TRACING'] = "1";
process.env['DISABLE_DEBUGGER'] = "1";

const grpcWorker = new Worker("./server.js");
const restWorker = new Worker("./rest-server.js")
const thriftWorker = new Worker("./thrift-server.js")

function cleanup() {
  restWorker.postMessage('cleanup');
  thriftWorker.postMessage('cleanup');
  process.exit(1);
}
