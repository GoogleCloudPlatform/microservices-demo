module github.com/GoogleCloudPlatform/microservices-demo/src/productcatalogservice

go 1.15

require (
	cloud.google.com/go v0.65.0
	contrib.go.opencensus.io/exporter/jaeger v0.2.0
	contrib.go.opencensus.io/exporter/stackdriver v0.5.0
	github.com/CSCI-2390-Project/privacy-go v1.99.0
	github.com/golang/protobuf v1.4.3
	github.com/google/go-cmp v0.5.2
	github.com/konsorten/go-windows-terminal-sequences v1.0.2 // indirect
	github.com/sirupsen/logrus v1.7.0
	github.com/stretchr/objx v0.1.1 // indirect
	github.com/uber/jaeger-client-go v2.21.1+incompatible // indirect
	go.opencensus.io v0.22.4
	golang.org/x/net v0.0.0-20201029055024-942e2f445f3c
	google.golang.org/grpc v1.32.0
)

replace google.golang.org/grpc => github.com/CSCI-2390-Project/grpc-go v1.99.0

replace google.golang.org/protobuf => github.com/CSCI-2390-Project/protobuf-go v1.99.0
