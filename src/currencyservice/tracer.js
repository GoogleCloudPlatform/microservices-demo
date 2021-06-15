'use strict';

const { NodeTracerProvider } = require('@opentelemetry/node');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { BatchSpanProcessor } = require('@opentelemetry/tracing');
const {
  CollectorTraceExporter,
} = require('@opentelemetry/exporter-collector-grpc');
const { GrpcInstrumentation } = require('@opentelemetry/instrumentation-grpc');
const { PinoInstrumentation } = require('@opentelemetry/instrumentation-pino');
const { Resource } = require('@opentelemetry/resources');
const { ResourceAttributes } = require('@opentelemetry/semantic-conventions');
const os = require('os');

const identifier = process.env.HOSTNAME || os.hostname();
const resource = new Resource({
  [ResourceAttributes.SERVICE_INSTANCE_ID]: identifier,
  [ResourceAttributes.SERVICE_NAME]: 'CurrencyService',
});

const traceProvider = new NodeTracerProvider({
  resource,
});

const traceExporter = new CollectorTraceExporter({
  url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
});

traceProvider.addSpanProcessor(new BatchSpanProcessor(traceExporter));
traceProvider.register();

registerInstrumentations({
  instrumentations: [
    new PinoInstrumentation({
      logHook: (_span, record) => {
        record['service.name'] =
          traceProvider.resource.attributes['service.name'];
      },
    }),
    new GrpcInstrumentation(),
  ],
});
