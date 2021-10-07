module github.com/GoogleCloudPlatform/microservices-demo/src/shippingservice

go 1.17

replace	github.com/Rookout/GoRook => /src/GoRook
//replace github.com/Rookout/GoRook => /Users/gilad/dev/GoRook

require (
	cloud.google.com/go v0.40.0
	contrib.go.opencensus.io/exporter/jaeger v0.2.0
	contrib.go.opencensus.io/exporter/stackdriver v0.5.0
	github.com/Rookout/GoRook v0.0.0
	github.com/golang/protobuf v1.4.2
	github.com/google/pprof v0.0.0-20190515194954-54271f7e092f // indirect
	github.com/sirupsen/logrus v1.8.1
	github.com/uber/jaeger-client-go v2.21.1+incompatible // indirect
	go.opencensus.io v0.21.0
	golang.org/x/net v0.0.0-20200602114024-627f9648deb9
	golang.org/x/sys v0.0.0-20210917161153-d61c044b1678 // indirect
	google.golang.org/api v0.7.1-0.20190709010654-aae1d1b89c27 // indirect
	google.golang.org/appengine v1.6.1 // indirect
	google.golang.org/genproto v0.0.0-20200526211855-cb27e3aa2013 // indirect
	google.golang.org/grpc v1.29.1
)

require (
	github.com/Jeffail/gabs v1.4.0 // indirect
	github.com/go-errors/errors v1.1.1 // indirect
	github.com/google/go-cmp v0.5.0 // indirect
	github.com/google/uuid v1.1.2 // indirect
	github.com/googleapis/gax-go/v2 v2.0.4 // indirect
	github.com/gorilla/websocket v1.4.2 // indirect
	github.com/hashicorp/golang-lru v0.5.4 // indirect
	github.com/mattn/go-isatty v0.0.12 // indirect
	golang.org/x/arch v0.0.0-20190927153633-4e8777c89be4 // indirect
	golang.org/x/oauth2 v0.0.0-20190604053449-0f29369cfe45 // indirect
	golang.org/x/sync v0.0.0-20190911185100-cd5d95a43a6e // indirect
	golang.org/x/text v0.3.2 // indirect
	golang.org/x/time v0.0.0-20201208040808-7e3f01d25324 // indirect
	google.golang.org/protobuf v1.25.0 // indirect
	gopkg.in/yaml.v2 v2.2.8 // indirect
)

replace git.apache.org/thrift.git v0.12.1-0.20190708170704-286eee16b147 => github.com/apache/thrift v0.12.1-0.20190708170704-286eee16b147
