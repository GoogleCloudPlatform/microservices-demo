'use strict'
const { NodeTracerProvider } = require('@opentelemetry/node')
const { BatchSpanProcessor } = require('@opentelemetry/tracing')
const { ZipkinExporter } = require('@opentelemetry/exporter-zipkin')
const { Resource, SERVICE_RESOURCE } = require('@opentelemetry/resources')
const os = require('os')

const identifier = process.env.HOSTNAME || os.hostname()
const instanceResource = new Resource({
 [SERVICE_RESOURCE.INSTANCE_ID]: identifier,
 [SERVICE_RESOURCE.NAME]: 'PaymentService'
})

const mergedResource = Resource.createTelemetrySDKResource().merge(instanceResource)

const NR_ZIPKIN_HEADERS = {
  'Api-Key': process.env.NEW_RELIC_API_KEY,
  'Data-Format': 'zipkin',
  'Data-Format-Version': '2',
}

const traceProvider = new NodeTracerProvider({
  resource: mergedResource
})

traceProvider.addSpanProcessor(
  new BatchSpanProcessor(
    new ZipkinExporter({
      url: process.env.NEW_RELIC_TRACE_URL,
      headers: NR_ZIPKIN_HEADERS,
      statusCodeTagName: 'otel.status_code',
      statusDescriptionTagName: 'otel.status_description'
    })
  )
)
traceProvider.register()
