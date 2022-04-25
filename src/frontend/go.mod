module github.com/GoogleCloudPlatform/microservices-demo/src/frontend

go 1.18

require (
	cloud.google.com/go v0.97.0
	github.com/golang/protobuf v1.5.2
	github.com/google/uuid v1.3.0
	github.com/gorilla/mux v1.8.0
	github.com/pkg/errors v0.9.1
	github.com/sirupsen/logrus v1.8.1
	go.opentelemetry.io/contrib/detectors/gcp v0.20.0
	go.opentelemetry.io/contrib/instrumentation/github.com/gorilla/mux/otelmux v0.20.0
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.20.0
	go.opentelemetry.io/contrib/instrumentation/net/http/httptrace/otelhttptrace v0.20.0
	go.opentelemetry.io/contrib/instrumentation/runtime v0.20.0
	go.opentelemetry.io/otel v0.20.0
	go.opentelemetry.io/otel/exporters/otlp v0.20.0
	go.opentelemetry.io/otel/metric v0.20.0
	go.opentelemetry.io/otel/sdk v0.20.0
	go.opentelemetry.io/otel/sdk/export/metric v0.20.0
	go.opentelemetry.io/otel/sdk/metric v0.20.0
	go.opentelemetry.io/otel/trace v0.20.0
	golang.org/x/net v0.0.0-20220403103023-749bd193bc2b
	google.golang.org/grpc v1.43.0
)

require (
	github.com/felixge/httpsnoop v1.0.1 // indirect
	github.com/grpc-ecosystem/grpc-gateway v1.16.0 // indirect
	go.opentelemetry.io/contrib v0.20.0 // indirect
	go.opentelemetry.io/proto/otlp v0.7.0 // indirect
	golang.org/x/oauth2 v0.0.0-20211104180415-d3ed0bb246c8 // indirect
	golang.org/x/sys v0.0.0-20211216021012-1d35b9e2eb4e // indirect
	golang.org/x/text v0.3.7 // indirect
	google.golang.org/genproto v0.0.0-20211206160659-862468c7d6e0 // indirect
	google.golang.org/protobuf v1.27.1 // indirect
)
