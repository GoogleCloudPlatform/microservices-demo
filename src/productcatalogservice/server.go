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
	{
		Id:          "OLJCESPC7Z",
		Name:        "Vintage Typewriter",
		Description: "This typewriter looks good in your living room.",
		Picture:     "/static/img/products/typewriter.jpg",
		PriceUsd:    &pb.MoneyAmount{Decimal: 67, Fractional: 99},
	},
	{
		Id:          "66VCHSJNUP",
		Name:        "Vintage Camera Lens",
		Description: "You won't have a camera to use it and it probably doesn't work anyway.",
		Picture:     "/static/img/products/camera-lens.jpg",
		PriceUsd:    &pb.MoneyAmount{Decimal: 12, Fractional: 49},
	},
	{
		Id:          "1YMWWN1N4O",
		Name:        "Home Barista Kit",
		Description: "Always wanted to brew coffee with Chemex and Aeropress at home?",
		Picture:     "/static/img/products/barista-kit.jpg",
		PriceUsd:    &pb.MoneyAmount{Decimal: 124, Fractional: 0},
	},
	{
		Id:          "L9ECAV7KIM",
		Name:        "Terrarium",
		Description: "This terrarium will looks great in your white painted living room.",
		Picture:     "/static/img/products/terrarium.jpg",
		PriceUsd:    &pb.MoneyAmount{Decimal: 36, Fractional: 45},
	},
	{
		Id:          "2ZYFJ3GM2N",
		Name:        "Film Camera",
		Description: "This camera looks like it's a film camera, but it's actually digital.",
		Picture:     "/static/img/products/film-camera.jpg",
		PriceUsd:    &pb.MoneyAmount{Decimal: 2245, Fractional: 0},
	},
	{
		Id:          "0PUK6V6EV0",
		Name:        "Vintage Record Player",
		Description: "It still works.",
		Picture:     "/static/img/products/record-player.jpg",
		PriceUsd:    &pb.MoneyAmount{Decimal: 65, Fractional: 50},
	},
	{
		Id:          "LS4PSXUNUM",
		Name:        "Metal Camping Mug",
		Description: "You probably don't go camping that often but this is better than plastic cups.",
		Picture:     "/static/img/products/camp-mug.jpg",
		PriceUsd:    &pb.MoneyAmount{Decimal: 24, Fractional: 33},
	},
	{
		Id:          "9SIQT8TOJO",
		Name:        "City Bike",
		Description: "This single gear bike probably cannot climb the hills of San Francisco.",
		Picture:     "/static/img/products/city-bike.jpg",
		PriceUsd:    &pb.MoneyAmount{Decimal: 789, Fractional: 50},
	},
	{
		Id:          "6E92ZMYYFZ",
		Name:        "Air Plant",
		Description: "Have you ever wondered whether air plants need water? Buy one and figure out.",
		Picture:     "/static/img/products/air-plant.jpg",
		PriceUsd:    &pb.MoneyAmount{Decimal: 12, Fractional: 30},
	},
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
	return nil, status.Errorf(codes.NotFound, "no product with ID %s", req.Id)
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
