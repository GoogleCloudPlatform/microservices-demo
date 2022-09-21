const { Resource } = require("@opentelemetry/resources");
const { SemanticResourceAttributes } = require("@opentelemetry/semantic-conventions");
const { NodeTracerProvider } = require("@opentelemetry/sdk-trace-node");
const { BatchSpanProcessor } = require("@opentelemetry/sdk-trace-base");
const { JaegerExporter } = require("@opentelemetry/exporter-jaeger");
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { GrpcInstrumentation } = require('@opentelemetry/instrumentation-grpc');


const resource =
    Resource.default().merge(
        new Resource({
            [SemanticResourceAttributes.SERVICE_NAME]: "payment",
            [SemanticResourceAttributes.SERVICE_VERSION]: "0.0.1",
        })
    );

const provider = new NodeTracerProvider({
    resource: resource,
});
const jaegerOptions = {
    endpoint: `http://${process.env.JAEGER_SERVICE_ADDR}/api/traces`
};
provider.addSpanProcessor(new BatchSpanProcessor(new JaegerExporter(jaegerOptions)));
provider.register();

registerInstrumentations({
    instrumentations: [new GrpcInstrumentation()]
})