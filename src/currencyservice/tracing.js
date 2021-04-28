const { NodeTracerProvider } = require('@opentelemetry/node');
const { B3MultiPropagator } = require('@opentelemetry/propagator-b3');
const { ZipkinExporter } = require('@opentelemetry/exporter-zipkin');
const { GrpcInstrumentation } = require('@opentelemetry/instrumentation-grpc');
const { BatchSpanProcessor, ConsoleSpanExporter } = require('@opentelemetry/tracing');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');

const provider = new NodeTracerProvider();
provider.register({
  propagator: new B3MultiPropagator(),
});

registerInstrumentations({
  instrumentations: [
    new GrpcInstrumentation(),
  ],
});

const exporter = new ZipkinExporter({
  serviceName: 'currencyservice',
  url: process.env.SIGNALFX_ENDPOINT_URL,
});

provider.addSpanProcessor(new BatchSpanProcessor(exporter));

