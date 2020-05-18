module github.com/signalfx/microservices-demo/src/shippingservice

go 1.14

require (
	cloud.google.com/go v0.40.0
	contrib.go.opencensus.io/exporter/ocagent v0.6.0
	contrib.go.opencensus.io/exporter/stackdriver v0.5.0
	github.com/golang/protobuf v1.3.2
	github.com/google/pprof v0.0.0-20190515194954-54271f7e092f // indirect
	github.com/konsorten/go-windows-terminal-sequences v1.0.2 // indirect
	github.com/sirupsen/logrus v1.4.2
	go.opencensus.io v0.22.0
	golang.org/x/net v0.0.0-20190628185345-da137c7871d7
	google.golang.org/api v0.7.1-0.20190709010654-aae1d1b89c27 // indirect
	google.golang.org/appengine v1.6.1 // indirect
	google.golang.org/grpc v1.22.0
)

replace git.apache.org/thrift.git v0.12.1-0.20190708170704-286eee16b147 => github.com/apache/thrift v0.12.1-0.20190708170704-286eee16b147
