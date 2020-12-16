'use strict'
const { NodeTracerProvider } = require('@opentelemetry/node')
const { BatchSpanProcessor } = require('@opentelemetry/tracing')
const { ZipkinExporter } = require('@opentelemetry/exporter-zipkin')
const { CollectorTraceExporter } =  require('@opentelemetry/exporter-collector-grpc')
const { Resource, SERVICE_RESOURCE } = require('@opentelemetry/resources')
const os = require('os')

const identifier = process.env.HOSTNAME || os.hostname()
const exportType = process.env.NEW_RELIC_DEMO_EXPORT_TYPE
const instanceResource = new Resource({
 [SERVICE_RESOURCE.INSTANCE_ID]: identifier,
 [SERVICE_RESOURCE.NAME]: 'CurrencyService-' + exportType
})

const mergedResource = Resource.createTelemetrySDKResource().merge(instanceResource)

const NR_ZIPKIN_HEADERS = {
  'Api-Key': process.env.NEW_RELIC_API_KEY,
  'Data-Format': 'zipkin',
  'Data-Format-Version': '2',
}

function getExporter(exporterType) {
  switch (exporterType) {
    case 'otlp':
      return new CollectorTraceExporter({
        url: process.env.OTEL_EXPORTER_OTLP_SPAN_ENDPOINT
      })
    case 'zipkin':
      return new ZipkinExporter({
        url: process.env.NEW_RELIC_TRACE_URL,
        headers: NR_ZIPKIN_HEADERS,
        statusCodeTagName: 'otel.status_code',
        statusDescriptionTagName: 'otel.status_description'
      })
    default:
      return null
  }
}

const exporter = getExporter(exportType)

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
