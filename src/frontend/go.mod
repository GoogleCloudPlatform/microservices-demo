module github.com/GoogleCloudPlatform/microservices-demo/src/frontend

go 1.15

require (
	github.com/golang/protobuf v1.4.3
	github.com/google/uuid v1.1.2
	github.com/gorilla/mux v1.8.0
	github.com/newrelic/newrelic-telemetry-sdk-go v0.4.0
	github.com/newrelic/opentelemetry-exporter-go v0.13.1-0.20201204162309-3cbb92367b23
	github.com/pkg/errors v0.9.1
	github.com/sirupsen/logrus v1.6.0
	go.opentelemetry.io/contrib/detectors/gcp v0.15.1
	go.opentelemetry.io/contrib/instrumentation/github.com/gorilla/mux/otelmux v0.15.1
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.15.1
	go.opentelemetry.io/contrib/instrumentation/net/http/httptrace/otelhttptrace v0.15.1
	go.opentelemetry.io/contrib/instrumentation/runtime v0.15.1
	go.opentelemetry.io/otel v0.15.0
	go.opentelemetry.io/otel/exporters/stdout v0.15.0
	go.opentelemetry.io/otel/sdk v0.15.0
	golang.org/x/net v0.0.0-20201209123823-ac852fbbde11
	google.golang.org/grpc v1.34.0
)
