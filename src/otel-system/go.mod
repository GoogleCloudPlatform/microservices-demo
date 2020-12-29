module github.com/GoogleCloudPlatform/microservices-demo/src/otel-system

go 1.15

require (
	github.com/google/uuid v1.1.2
	github.com/newrelic/newrelic-telemetry-sdk-go v0.5.1
	github.com/newrelic/opentelemetry-exporter-go v0.14.0
	github.com/sirupsen/logrus v1.7.0
	go.opentelemetry.io/contrib/detectors/gcp v0.15.1
	go.opentelemetry.io/contrib/instrumentation/host v0.15.1
	go.opentelemetry.io/contrib/instrumentation/runtime v0.15.1
	go.opentelemetry.io/otel v0.15.0
	go.opentelemetry.io/otel/exporters/otlp v0.15.0
	go.opentelemetry.io/otel/exporters/stdout v0.15.0
	go.opentelemetry.io/otel/sdk v0.15.0
)
