module github.com/GoogleCloudPlatform/microservices-demo/src/frontend

go 1.14

require (
	cloud.google.com/go v0.63.0
	github.com/golang/protobuf v1.4.2
	github.com/google/uuid v1.1.1
	github.com/gorilla/mux v1.8.0
	github.com/newrelic/newrelic-telemetry-sdk-go v0.4.0
	github.com/newrelic/opentelemetry-exporter-go v0.1.1-0.20200910144408-6586c0322d09
	github.com/pkg/errors v0.9.1
	github.com/sirupsen/logrus v1.6.0
	go.opentelemetry.io/contrib/instrumentation/github.com/gorilla/mux v0.11.0
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc v0.11.0
	go.opentelemetry.io/contrib/instrumentation/net/http/httptrace v0.11.0
	go.opentelemetry.io/otel v0.11.0
	go.opentelemetry.io/otel/exporters/stdout v0.11.0
	go.opentelemetry.io/otel/sdk v0.11.0
	golang.org/x/net v0.0.0-20200813134508-3edf25e44fcc
	google.golang.org/grpc v1.31.0
)
