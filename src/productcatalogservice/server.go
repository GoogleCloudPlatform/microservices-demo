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
	"github.com/golang/protobuf/jsonpb"
	"go.opencensus.io/exporter/stackdriver"
	"go.opencensus.io/plugin/ocgrpc"
	"go.opencensus.io/trace"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var port = flag.Int("port", 3550, "port to listen at")

const catalogJSON = `{
	"products": [
  	{
    	"id": "OLJCESPC7Z",
    	"name": "Vintage Typewriter",
    	"description": "This typewriter looks good in your living room.",
    	"picture": "/static/img/products/typewriter.jpg",
    	"priceUsd": {
      	"currencyCode": "USD",
      	"units": 67,
      	"nanos": 990000000
    	}
  	},
  	{
    	"id": "66VCHSJNUP",
    	"name": "Vintage Camera Lens",
    	"description": "You won't have a camera to use it and it probably doesn't work anyway.",
    	"picture": "/static/img/products/camera-lens.jpg",
    	"priceUsd": {
      	"currencyCode": "USD",
      	"units": 12,
      	"nanos": 490000000
    	}
  	},
  	{
    	"id": "1YMWWN1N4O",
    	"name": "Home Barista Kit",
    	"description": "Always wanted to brew coffee with Chemex and Aeropress at home?",
    	"picture": "/static/img/products/barista-kit.jpg",
    	"priceUsd": {
      	"currencyCode": "USD",
      	"units": 124
    	}
  	},
  	{
    	"id": "L9ECAV7KIM",
    	"name": "Terrarium",
    	"description": "This terrarium will looks great in your white painted living room.",
    	"picture": "/static/img/products/terrarium.jpg",
    	"priceUsd": {
      	"currencyCode": "USD",
      	"units": 36,
      	"nanos": 450000000
    	}
  	},
  	{
    	"id": "2ZYFJ3GM2N",
    	"name": "Film Camera",
    	"description": "This camera looks like it's a film camera, but it's actually digital.",
    	"picture": "/static/img/products/film-camera.jpg",
    	"priceUsd": {
      	"currencyCode": "USD",
      	"units": 2245
    	}
  	},
  	{
    	"id": "0PUK6V6EV0",
    	"name": "Vintage Record Player",
    	"description": "It still works.",
    	"picture": "/static/img/products/record-player.jpg",
    	"priceUsd": {
      	"currencyCode": "USD",
      	"units": 65,
      	"nanos": 500000000
    	}
  	},
  	{
    	"id": "LS4PSXUNUM",
    	"name": "Metal Camping Mug",
    	"description": "You probably don't go camping that often but this is better than plastic cups.",
    	"picture": "/static/img/products/camp-mug.jpg",
    	"priceUsd": {
      	"currencyCode": "USD",
      	"units": 24,
      	"nanos": 330000000
    	}
  	},
  	{
    	"id": "9SIQT8TOJO",
    	"name": "City Bike",
    	"description": "This single gear bike probably cannot climb the hills of San Francisco.",
    	"picture": "/static/img/products/city-bike.jpg",
    	"priceUsd": {
      	"currencyCode": "USD",
      	"units": 789,
      	"nanos": 500000000
    	}
  	},
  	{
    	"id": "6E92ZMYYFZ",
    	"name": "Air Plant",
    	"description": "Have you ever wondered whether air plants need water? Buy one and figure out.",
    	"picture": "/static/img/products/air-plant.jpg",
    	"priceUsd": {
      	"currencyCode": "USD",
      	"units": 12,
      	"nanos": 300000000
    	}
  	}
	]
}`

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
			ProjectID: "oval-time-515",
		}); err != nil {
			log.Printf("warn: failed to start profiler: %+v", err)
			d := time.Second * 10 * time.Duration(i)
			log.Printf("sleeping %v to retry initializing stackdriver profiler", d)
			time.Sleep(d)
			continue
		}
		return
	}
	log.Printf("warning: could not initialize stackdriver profiler after retrying, giving up")
}

type productCatalog struct{}

func (p *productCatalog) catalog() []*pb.Product {
	var cat pb.ListProductsResponse
	if err := jsonpb.UnmarshalString(catalogJSON, &cat); err != nil {
		log.Printf("warning: failed to parse the product catalog: %v", err)
		return nil
	}
	return cat.Products
}

func (p *productCatalog) ListProducts(context.Context, *pb.Empty) (*pb.ListProductsResponse, error) {
	return &pb.ListProductsResponse{Products: p.catalog()}, nil
}

func (p *productCatalog) GetProduct(ctx context.Context, req *pb.GetProductRequest) (*pb.Product, error) {
	var found *pb.Product
	for i := 0; i < len(p.catalog()); i++ {
		if req.Id == p.catalog()[i].Id {
			found = p.catalog()[i]
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
	for _, p := range p.catalog() {
		if strings.Contains(strings.ToLower(p.Name), strings.ToLower(req.Query)) ||
			strings.Contains(strings.ToLower(p.Description), strings.ToLower(req.Query)) {
			ps = append(ps, p)
		}
	}
	return &pb.SearchProductsResponse{Results: ps}, nil
}
