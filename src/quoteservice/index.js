'use strict'

const opentelemetry = require("@opentelemetry/sdk-node");
const { ZipkinExporter } = require('@opentelemetry/exporter-zipkin');
const { PrometheusExporter } = require("@opentelemetry/exporter-prometheus");

const zipkinExporter = new ZipkinExporter({
  url: 'your-zipkin-url', // send this to the zipkin trace api endpoint
  serviceName: 'quoteservice'
})
// we need to export the metrics here
const prometheusExporter = new PrometheusExporter({ startServer: true })

const sdk = new opentelemetry.NodeSDK({
  traceExporter: zipkinExporter,
  metricExporter: prometheusExporter,
})

sdk
.start()
.then(() => {
  const express = require('express')

  const app = express()

  app.use('/', (req, res, next) => {
    res.json({quote: `stoicism did nothing wrong`})
    res.end()
  })

  app.listen(3000)
})
