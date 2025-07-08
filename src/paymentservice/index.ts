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

import logger from './logger';
import PaymentServer from './server'; // Updated to import PaymentServer (Express-based)

// OpenTelemetry and Profiler imports
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { OTLPTraceExporter } from '@opentelemetry/exporter-otlp-grpc'; // Still using gRPC exporter for OTel
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

const profiler = require('@google-cloud/profiler');

if (process.env.DISABLE_PROFILER) {
  logger.info('Profiler disabled.');
} else {
  logger.info('Profiler enabled.');
  profiler.start({
    serviceContext: {
      service: 'paymentservice',
      version: '1.0.0',
    },
  });
}

if (process.env.ENABLE_TRACING === '1') {
  logger.info('Tracing enabled for PaymentService (REST).');
  const provider = new NodeTracerProvider({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'paymentservice',
    }),
  });

  const collectorUrl = process.env.COLLECTOR_SERVICE_ADDR;
  if (collectorUrl) {
    // The OTLP exporter can still be gRPC, even if the service itself is REST
    provider.addSpanProcessor(new SimpleSpanProcessor(new OTLPTraceExporter({ url: collectorUrl })));
    provider.register();
    logger.info(`Tracing will be exported to: ${collectorUrl}`);
  } else {
    logger.warn('Collector service address not set for OTLPTraceExporter. Tracing will not be exported.');
  }

  registerInstrumentations({
    instrumentations: [
      new HttpInstrumentation(), // Instrumentation for outgoing HTTP requests
      new ExpressInstrumentation(), // Instrumentation for the Express server itself
    ],
  });
} else {
  logger.info('Tracing disabled for PaymentService.');
}

const PORT: string | undefined = process.env.PORT;
// PROTO_PATH is no longer needed for the REST server initialization

const server = new PaymentServer(PORT); // Initialize the Express server

server.listen();
