package main

import (
	"bytes"
	"context"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net"
	"strings"
	"time"

	pb "./genproto"

	"cloud.google.com/go/profiler"
	"github.com/golang/protobuf/jsonpb"
	"go.opencensus.io/exporter/stackdriver"
	"go.opencensus.io/plugin/ocgrpc"
	"go.opencensus.io/trace"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var (
	catalogJSON []byte

	port = flag.Int("port", 3550, "port to listen at")
)

func init() {
	c, err := ioutil.ReadFile("products.json")
	if err != nil {
		log.Fatalf("failed to open product catalog json file: %v", err)
	}
	catalogJSON = c
	log.Printf("successfully parsed product catalog json")
}

func main() {
	go initTracing()
	go initProfiling("productcatalogservice", "1.0.0")
	flag.Parse()

	log.Printf("starting grpc server at :%d", *port)
	run(*port)
	select {}
}

func run(port int) string {
	l, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		log.Fatal(err)
	}
	srv := grpc.NewServer(grpc.StatsHandler(&ocgrpc.ServerHandler{}))
	pb.RegisterProductCatalogServiceServer(srv, &productCatalog{})
	go srv.Serve(l)
	return l.Addr().String()
}

func initTracing() {
	// TODO(ahmetb) this method is duplicated in other microservices using Go
	// since they are not sharing packages.
	for i := 1; i <= 3; i++ {
		exporter, err := stackdriver.NewExporter(stackdriver.Options{})
		if err != nil {
			log.Printf("info: failed to initialize stackdriver exporter: %+v", err)
		} else {
			trace.RegisterExporter(exporter)
			trace.ApplyConfig(trace.Config{DefaultSampler: trace.AlwaysSample()})
			log.Print("registered stackdriver tracing")
			return
		}
		d := time.Second * 10 * time.Duration(i)
		log.Printf("sleeping %v to retry initializing stackdriver exporter", d)
		time.Sleep(d)
	}
	log.Printf("warning: could not initialize stackdriver exporter after retrying, giving up")
}

func initProfiling(service, version string) {
	// TODO(ahmetb) this method is duplicated in other microservices using Go
	// since they are not sharing packages.
	for i := 1; i <= 3; i++ {
		if err := profiler.Start(profiler.Config{
			Service:        service,
			ServiceVersion: version,
			// ProjectID must be set if not running on GCP.
			// ProjectID: "my-project",
		}); err != nil {
			log.Printf("warn: failed to start profiler: %+v", err)
		} else {
			log.Print("started stackdriver profiler")
			return
		}
		d := time.Second * 10 * time.Duration(i)
		log.Printf("sleeping %v to retry initializing stackdriver profiler", d)
		time.Sleep(d)
	}
	log.Printf("warning: could not initialize stackdriver profiler after retrying, giving up")
}

type productCatalog struct{}

func parseCatalog() []*pb.Product {
	var cat pb.ListProductsResponse

	if err := jsonpb.Unmarshal(bytes.NewReader(catalogJSON), &cat); err != nil {
		log.Printf("warning: failed to parse the catalog JSON: %v", err)
		return nil
	}
	return cat.Products
}

func (p *productCatalog) ListProducts(context.Context, *pb.Empty) (*pb.ListProductsResponse, error) {
	return &pb.ListProductsResponse{Products: parseCatalog()}, nil
}

func (p *productCatalog) GetProduct(ctx context.Context, req *pb.GetProductRequest) (*pb.Product, error) {
	var found *pb.Product
	for i := 0; i < len(parseCatalog()); i++ {
		if req.Id == parseCatalog()[i].Id {
			found = parseCatalog()[i]
		}
	}
	if found == nil {
		return nil, status.Errorf(codes.NotFound, "no product with ID %s", req.Id)
	}
	return found, nil
}

func (p *productCatalog) SearchProducts(ctx context.Context, req *pb.SearchProductsRequest) (*pb.SearchProductsResponse, error) {
	// Intepret query as a substring match in name or description.
	var ps []*pb.Product
	for _, p := range parseCatalog() {
		if strings.Contains(strings.ToLower(p.Name), strings.ToLower(req.Query)) ||
			strings.Contains(strings.ToLower(p.Description), strings.ToLower(req.Query)) {
			ps = append(ps, p)
		}
	}
	return &pb.SearchProductsResponse{Results: ps}, nil
}
