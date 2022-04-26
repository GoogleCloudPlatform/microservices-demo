module github.com/GoogleCloudPlatform/microservices-demo/src/productcatalogservice

go 1.18

require (
	github.com/golang/protobuf v1.5.2
	github.com/google/go-cmp v0.5.7
	github.com/google/uuid v1.1.2
	github.com/sirupsen/logrus v1.8.1
	go.opentelemetry.io/contrib/detectors/gcp v0.14.0
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.14.0
	go.opentelemetry.io/otel v0.14.0
	go.opentelemetry.io/otel/exporters/otlp v0.14.0
	go.opentelemetry.io/otel/exporters/stdout v0.14.0
	go.opentelemetry.io/otel/exporters/trace/jaeger v0.14.0
	go.opentelemetry.io/otel/sdk v0.14.0
	golang.org/x/net v0.0.0-20220403103023-749bd193bc2b
	google.golang.org/grpc v1.43.0
)

require (
	cloud.google.com/go v0.99.0 // indirect
	github.com/DataDog/sketches-go v0.0.1 // indirect
	github.com/apache/thrift v0.13.0 // indirect
	github.com/gogo/protobuf v1.3.1 // indirect
	go.opentelemetry.io/contrib v0.14.0 // indirect
	golang.org/x/sync v0.0.0-20210220032951-036812b2e83c // indirect
	golang.org/x/sys v0.0.0-20211216021012-1d35b9e2eb4e // indirect
	golang.org/x/text v0.3.7 // indirect
	google.golang.org/api v0.61.0 // indirect
	google.golang.org/genproto v0.0.0-20211206160659-862468c7d6e0 // indirect
	google.golang.org/protobuf v1.27.1 // indirect
)
