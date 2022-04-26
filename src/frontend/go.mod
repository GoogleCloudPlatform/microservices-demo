module github.com/GoogleCloudPlatform/microservices-demo/src/frontend

go 1.18

require (
	cloud.google.com/go v0.100.2
	cloud.google.com/go/compute v1.6.1
	github.com/golang/protobuf v1.5.2
	github.com/google/uuid v1.3.0
	github.com/gorilla/mux v1.8.0
	github.com/pkg/errors v0.9.1
	github.com/sirupsen/logrus v1.8.1
	go.opentelemetry.io/contrib/instrumentation/github.com/gorilla/mux/otelmux v0.31.0
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.31.0
	go.opentelemetry.io/contrib/instrumentation/net/http/httptrace/otelhttptrace v0.31.0
	go.opentelemetry.io/contrib/instrumentation/runtime v0.31.0
	go.opentelemetry.io/otel v1.6.3
	go.opentelemetry.io/otel/exporters/otlp/otlpmetric v0.28.0
	go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc v0.28.0
	go.opentelemetry.io/otel/exporters/otlp/otlptrace v1.6.1
	go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc v1.6.1
	go.opentelemetry.io/otel/metric v0.28.0
	go.opentelemetry.io/otel/sdk v1.6.3
	go.opentelemetry.io/otel/sdk/metric v0.28.0
	go.opentelemetry.io/otel/trace v1.6.3
	golang.org/x/net v0.0.0-20220412020605-290c469a71a5
	google.golang.org/grpc v1.45.0
)

require (
	github.com/cenkalti/backoff/v4 v4.1.2 // indirect
	github.com/felixge/httpsnoop v1.0.2 // indirect
	github.com/go-logr/logr v1.2.3 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/grpc-ecosystem/grpc-gateway/v2 v2.7.0 // indirect
	github.com/konsorten/go-windows-terminal-sequences v1.0.3 // indirect
	go.opentelemetry.io/otel/exporters/otlp/internal/retry v1.6.3 // indirect
	go.opentelemetry.io/proto/otlp v0.14.0 // indirect
	golang.org/x/sys v0.0.0-20220412211240-33da011f77ad // indirect
	golang.org/x/text v0.3.7 // indirect
	google.golang.org/genproto v0.0.0-20220421151946-72621c1f0bd3 // indirect
	google.golang.org/protobuf v1.28.0 // indirect
)
