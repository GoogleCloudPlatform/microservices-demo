package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"strings"

	pb "./genproto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var port = flag.Int("port", 3550, "port to listen at")

var catalog = []*pb.Product{
	{Id: 1, Name: "shirt", Description: "nice shirt", Picture: "picture1", PriceUsd: &pb.MoneyAmount{Decimal: 53}},
	{Id: 2, Name: "pants", Description: "nice pants", Picture: "picture2", PriceUsd: &pb.MoneyAmount{Decimal: 81}},
	{Id: 3, Name: "hat", Description: "nice hat", Picture: "picture3", PriceUsd: &pb.MoneyAmount{Decimal: 20}},
}

func main() {
	flag.Parse()
	run(*port)
	select {}
}

func run(port int) string {
	l, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		log.Fatal(err)
	}
	srv := grpc.NewServer()
	pb.RegisterProductCatalogServiceServer(srv, &productCatalog{})
	go srv.Serve(l)
	return l.Addr().String()
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
	return nil, status.Errorf(codes.NotFound, "no product with ID %d", req.Id)
}

func (p *productCatalog) SearchProducts(ctx context.Context, req *pb.SearchProductsRequest) (*pb.SearchProductsResponse, error) {
	// Intepret query as a substring match in name or description.
	var ps []*pb.Product
	for _, p := range catalog {
		if strings.Contains(p.Name, req.Query) || strings.Contains(p.Description, req.Query) {
			ps = append(ps, p)
		}
	}
	return &pb.SearchProductsResponse{Results: ps}, nil
}
