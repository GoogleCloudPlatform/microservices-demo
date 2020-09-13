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

const api = require("@opentelemetry/api");
const { NodeTracerProvider } = require('@opentelemetry/node');
const { B3Propagator } = require("@opentelemetry/core");
const { ZipkinExporter } = require('@opentelemetry/exporter-zipkin');
const { BatchSpanProcessor } = require('@opentelemetry/tracing');

api.propagation.setGlobalPropagator(new B3Propagator());

const provider = new NodeTracerProvider();
provider.register({
  propagator: new B3Propagator(),
});

const exporter = new ZipkinExporter({
  serviceName: 'paymentservice',
  url: process.env.SIGNALFX_ENDPOINT_URL,
});

const tracer = provider.getTracer('paymentservice')
provider.addSpanProcessor(new BatchSpanProcessor(exporter));


const path = require('path');
const HipsterShopServer = require('./server');

const PORT = process.env['PORT'];
const PROTO_PATH = path.join(__dirname, '/proto/');

const server = new HipsterShopServer(PROTO_PATH, PORT);

server.listen();
