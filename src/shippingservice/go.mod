module github.com/GoogleCloudPlatform/microservices-demo/src/shippingservice

go 1.13

require (
	cloud.google.com/go v0.52.0
	contrib.go.opencensus.io/exporter/jaeger v0.2.0
	contrib.go.opencensus.io/exporter/prometheus v0.1.0
	contrib.go.opencensus.io/exporter/stackdriver v0.12.9
	contrib.go.opencensus.io/exporter/zipkin v0.1.1
	github.com/golang/protobuf v1.3.2
	github.com/openzipkin/zipkin-go v0.2.2
	github.com/sirupsen/logrus v1.4.2
	go.opencensus.io v0.22.2
	golang.org/x/net v0.0.0-20200114155413-6afb5195e5aa
	google.golang.org/grpc v1.27.0
)
