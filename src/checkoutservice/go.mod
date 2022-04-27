module github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice

go 1.18

require (
	github.com/golang/protobuf v1.5.2
	github.com/google/uuid v1.3.0
	github.com/sirupsen/logrus v1.8.1
	github.com/pkg/errors v0.9.1
	go.opentelemetry.io/otel v1.6.3
	go.opentelemetry.io/otel/exporters/otlp/otlptrace v1.6.3
	go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc v1.6.3
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.31.0
	go.opentelemetry.io/otel/sdk v1.6.3
	golang.org/x/net v0.0.0-20220412020605-290c469a71a5
	google.golang.org/grpc v1.45.0
)

require (
	github.com/cenkalti/backoff/v4 v4.1.2 // indirect
	github.com/go-logr/logr v1.2.3 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/golang/groupcache v0.0.0-20200121045136-8c9f03a8e57e // indirect
	github.com/grpc-ecosystem/grpc-gateway/v2 v2.7.0 // indirect
	go.opentelemetry.io/otel/exporters/otlp/internal/retry v1.6.3 // indirect
	go.opentelemetry.io/otel/trace v1.6.3 // indirect
	go.opentelemetry.io/proto/otlp v0.15.0 // indirect
	golang.org/x/sys v0.0.0-20211216021012-1d35b9e2eb4e // indirect
	golang.org/x/text v0.3.7 // indirect
	google.golang.org/genproto v0.0.0-20211206160659-862468c7d6e0 // indirect
	google.golang.org/protobuf v1.28.0 // indirect
)
