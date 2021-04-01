// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"bytes"
	"context"
	"flag"
	"fmt"
	"io/ioutil"
	"net"
	"os"
	"os/signal"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/golang/protobuf/jsonpb"
	pb "github.com/signalfx/microservices-demo/src/productcatalogservice/genproto"
	"github.com/signalfx/splunk-otel-go/distro"
	"github.com/sirupsen/logrus"
	"go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
	"go.opentelemetry.io/otel/trace"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var (
	cat          pb.ListProductsResponse
	catalogMutex *sync.Mutex
	logger       *logrus.Logger
	extraLatency time.Duration

	port = "3550"

	reloadCatalog bool
)

func init() {
	logger = logrus.New()
	logger.Formatter = &logrus.JSONFormatter{
		FieldMap: logrus.FieldMap{
			logrus.FieldKeyTime:  "timestamp",
			logrus.FieldKeyLevel: "severity",
			logrus.FieldKeyMsg:   "message",
		},
		TimestampFormat: time.RFC3339Nano,
	}
	logger.Out = os.Stdout
	catalogMutex = &sync.Mutex{}
	err := readCatalogFile(context.Background(), &cat)
	if err != nil {
		logger.Warnf("could not parse product catalog")
	}
}

func main() {
	if os.Getenv("DISABLE_TRACING") == "" {
		logger.Info("Tracing enabled.")
		stopTracing := initTracing()
		defer stopTracing()
	} else {
		logger.Info("Tracing disabled.")
	}

	flag.Parse()

	// set injected latency
	if s := os.Getenv("EXTRA_LATENCY"); s != "" {
		v, err := time.ParseDuration(s)
		if err != nil {
			logger.Fatalf("failed to parse EXTRA_LATENCY (%s) as time.Duration: %+v", v, err)
		}
		extraLatency = v
		logger.Infof("extra latency enabled (duration: %v)", extraLatency)
	} else {
		extraLatency = time.Duration(0)
	}

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGUSR1, syscall.SIGUSR2)
	go func() {
		for {
			sig := <-sigs
			logger.Printf("Received signal: %s", sig)
			if sig == syscall.SIGUSR1 {
				reloadCatalog = true
				logger.Infof("Enable catalog reloading")
			} else {
				reloadCatalog = false
				logger.Infof("Disable catalog reloading")
			}
		}
	}()

	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}
	logger.Infof("starting grpc server at :%s", port)
	run(port)
	select {}
}

func run(port string) string {
	l, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		logger.Fatal(err)
	}

	var srv *grpc.Server
	srv = grpc.NewServer(
		grpc.UnaryInterceptor(otelgrpc.UnaryServerInterceptor()),
		grpc.StreamInterceptor(otelgrpc.StreamServerInterceptor()),
	)

	svc := &productCatalog{}

	pb.RegisterProductCatalogServiceServer(srv, svc)
	healthpb.RegisterHealthServer(srv, svc)
	go srv.Serve(l)
	return l.Addr().String()
}

func initTracing() func() {
	sdk, err := distro.Run(distro.WithServiceName("productcatalogservice"))
	if err != nil {
		panic(err)
	}

	logger.Info("otel initialization completed.")
	return func() {
		if err := sdk.Shutdown(context.Background()); err != nil {
			panic(err)
		}
	}
}

type productCatalog struct{}

func readCatalogFile(ctx context.Context, catalog *pb.ListProductsResponse) error {
	log := logger.WithFields(getTraceLogFields(ctx))
	catalogMutex.Lock()
	defer catalogMutex.Unlock()
	catalogJSON, err := ioutil.ReadFile("products.json")
	if err != nil {
		log.Fatalf("failed to open product catalog json file: %v", err)
		return err
	}
	if err := jsonpb.Unmarshal(bytes.NewReader(catalogJSON), catalog); err != nil {
		log.Warnf("failed to parse the catalog JSON: %v", err)
		return err
	}
	log.Info("successfully parsed product catalog json")
	return nil
}

func parseCatalog(ctx context.Context) []*pb.Product {
	if reloadCatalog || len(cat.Products) == 0 {
		err := readCatalogFile(ctx, &cat)
		if err != nil {
			return []*pb.Product{}
		}
	}
	return cat.Products
}

func (p *productCatalog) Check(ctx context.Context, req *healthpb.HealthCheckRequest) (*healthpb.HealthCheckResponse, error) {
	return &healthpb.HealthCheckResponse{Status: healthpb.HealthCheckResponse_SERVING}, nil
}

func (p *productCatalog) Watch(req *healthpb.HealthCheckRequest, ws healthpb.Health_WatchServer) error {
	return status.Errorf(codes.Unimplemented, "health check via Watch not implemented")
}

func (p *productCatalog) ListProducts(ctx context.Context, _ *pb.Empty) (*pb.ListProductsResponse, error) {
	time.Sleep(extraLatency)
	return &pb.ListProductsResponse{Products: parseCatalog(ctx)}, nil
}

func (p *productCatalog) GetProduct(ctx context.Context, req *pb.GetProductRequest) (*pb.Product, error) {
	time.Sleep(extraLatency)
	var found *pb.Product
	for i := 0; i < len(parseCatalog(ctx)); i++ {
		if req.Id == parseCatalog(ctx)[i].Id {
			found = parseCatalog(ctx)[i]
		}
	}
	if found == nil {
		return nil, status.Errorf(codes.NotFound, "no product with ID %s", req.Id)
	}
	return found, nil
}

func (p *productCatalog) SearchProducts(ctx context.Context, req *pb.SearchProductsRequest) (*pb.SearchProductsResponse, error) {
	time.Sleep(extraLatency)
	// Intepret query as a substring match in name or description.
	var ps []*pb.Product
	for _, p := range parseCatalog(ctx) {
		if strings.Contains(strings.ToLower(p.Name), strings.ToLower(req.Query)) ||
			strings.Contains(strings.ToLower(p.Description), strings.ToLower(req.Query)) {
			ps = append(ps, p)
		}
	}
	return &pb.SearchProductsResponse{Results: ps}, nil
}

func getTraceLogFields(ctx context.Context) logrus.Fields {
	fields := logrus.Fields{}
	if span := trace.SpanFromContext(ctx); span != nil {
		spanCtx := span.SpanContext()
		fields["trace_id"] = spanCtx.TraceID().String()
		fields["span_id"] = spanCtx.SpanID().String()
		fields["service.name"] = "productcatalogservice"
	}
	return fields
}
