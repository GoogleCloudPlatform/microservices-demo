'use strict'
const { NodeTracerProvider } = require('@opentelemetry/node')
const { BatchSpanProcessor } = require('@opentelemetry/tracing')
const { CollectorTraceExporter } =  require('@opentelemetry/exporter-collector-grpc')
const { Resource, SERVICE_RESOURCE } = require('@opentelemetry/resources')
const os = require('os')

const identifier = process.env.HOSTNAME || os.hostname()
const instanceResource = new Resource({
 [SERVICE_RESOURCE.INSTANCE_ID]: identifier,
 [SERVICE_RESOURCE.NAME]: 'PaymentService'
})

const mergedResource = Resource.createTelemetrySDKResource().merge(instanceResource)

function getExporter() {
  return new CollectorTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_SPAN_ENDPOINT
  })
}

const exporter = getExporter()

if (exporter != null)
{
  const traceProvider = new NodeTracerProvider({
    resource: mergedResource
  })

  traceProvider.addSpanProcessor(
    new BatchSpanProcessor(exporter)
  )

  traceProvider.register()
}
