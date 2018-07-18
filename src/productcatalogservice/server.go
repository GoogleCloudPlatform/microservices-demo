package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"strings"
	"time"

	pb "./genproto"
	"cloud.google.com/go/profiler"
	"go.opencensus.io/exporter/stackdriver"
	"go.opencensus.io/plugin/ocgrpc"
	"go.opencensus.io/trace"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var port = flag.Int("port", 3550, "port to listen at")

var catalog = []*pb.Product{
	{
		Id:          "OLJCESPC7Z",
		Name:        "Vintage Typewriter",
		Description: "This typewriter looks good in your living room.",
		Picture:     "/static/img/products/typewriter.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 67, Nanos: 990000000},
	},
	{
		Id:          "66VCHSJNUP",
		Name:        "Vintage Camera Lens",
		Description: "You won't have a camera to use it and it probably doesn't work anyway.",
		Picture:     "/static/img/products/camera-lens.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 12, Nanos: 490000000},
	},
	{
		Id:          "1YMWWN1N4O",
		Name:        "Home Barista Kit",
		Description: "Always wanted to brew coffee with Chemex and Aeropress at home?",
		Picture:     "/static/img/products/barista-kit.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 124, Nanos: 0},
	},
	{
		Id:          "L9ECAV7KIM",
		Name:        "Terrarium",
		Description: "This terrarium will looks great in your white painted living room.",
		Picture:     "/static/img/products/terrarium.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 36, Nanos: 450000000},
	},
	{
		Id:          "2ZYFJ3GM2N",
		Name:        "Film Camera",
		Description: "This camera looks like it's a film camera, but it's actually digital.",
		Picture:     "/static/img/products/film-camera.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 2245, Nanos: 00000000},
	},
	{
		Id:          "0PUK6V6EV0",
		Name:        "Vintage Record Player",
		Description: "It still works.",
		Picture:     "/static/img/products/record-player.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 65, Nanos: 500000000},
	},
	{
		Id:          "LS4PSXUNUM",
		Name:        "Metal Camping Mug",
		Description: "You probably don't go camping that often but this is better than plastic cups.",
		Picture:     "/static/img/products/camp-mug.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 24, Nanos: 330000000},
	},
	{
		Id:          "9SIQT8TOJO",
		Name:        "City Bike",
		Description: "This single gear bike probably cannot climb the hills of San Francisco.",
		Picture:     "/static/img/products/city-bike.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 789, Nanos: 500000000},
	},
	{
		Id:          "6E92ZMYYFZ",
		Name:        "Air Plant",
		Description: "Have you ever wondered whether air plants need water? Buy one and figure out.",
		Picture:     "/static/img/products/air-plant.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 12, Nanos: 300000000},
	},
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

func (p *productCatalog) ListProducts(context.Context, *pb.Empty) (*pb.ListProductsResponse, error) {
	return &pb.ListProductsResponse{Products: catalog}, nil
}

func (p *productCatalog) GetProduct(ctx context.Context, req *pb.GetProductRequest) (*pb.Product, error) {
	for _, p := range catalog {
		if req.Id == p.Id {
			return p, nil
		}
	}
	return nil, status.Errorf(codes.NotFound, "no product with ID %s", req.Id)
}

func (p *productCatalog) SearchProducts(ctx context.Context, req *pb.SearchProductsRequest) (*pb.SearchProductsResponse, error) {
	// Intepret query as a substring match in name or description.
	var ps []*pb.Product
	for _, p := range catalog {
		if strings.Contains(strings.ToLower(p.Name), strings.ToLower(req.Query)) ||
			strings.Contains(strings.ToLower(p.Description), strings.ToLower(req.Query)) {
			ps = append(ps, p)
		}
	}
	return &pb.SearchProductsResponse{Results: ps}, nil
}
