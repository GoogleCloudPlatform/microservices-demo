module github.com/GoogleCloudPlatform/microservices-demo/src/frontend

go 1.14

require (
	github.com/golang/protobuf v1.4.2
	github.com/google/uuid v1.1.1
	github.com/gorilla/mux v1.8.0
	github.com/newrelic/newrelic-telemetry-sdk-go v0.4.0
	github.com/newrelic/opentelemetry-exporter-go v0.13.0
	github.com/pkg/errors v0.9.1
	github.com/sirupsen/logrus v1.6.0
	go.opentelemetry.io/contrib/detectors/gcp v0.13.0
	go.opentelemetry.io/contrib/instrumentation/github.com/gorilla/mux/otelmux v0.13.0
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.13.0
	go.opentelemetry.io/contrib/instrumentation/net/http/httptrace/otelhttptrace v0.13.0
	go.opentelemetry.io/otel v0.13.0
	go.opentelemetry.io/otel/exporters/stdout v0.13.0
	go.opentelemetry.io/otel/sdk v0.13.0
	golang.org/x/net v0.0.0-20200927032502-5d4f70055728
	google.golang.org/grpc v1.32.0
)
