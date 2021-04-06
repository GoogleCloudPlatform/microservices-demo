const api = require("@opentelemetry/api");
const { NodeTracerProvider } = require('@opentelemetry/node');
const { B3Propagator } = require("@opentelemetry/core");
const { ZipkinExporter } = require('@opentelemetry/exporter-zipkin');
const { BatchSpanProcessor, ConsoleSpanExporter } = require('@opentelemetry/tracing');

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

const CONSOLE_SPAN = process.env['CONSOLE_SPAN'];
if (CONSOLE_SPAN === 'true') {
  provider.addSpanProcessor(new BatchSpanProcessor(new ConsoleSpanExporter(), { bufferTimeout: 1000 }));
}

module.exports = {
  tracer
}