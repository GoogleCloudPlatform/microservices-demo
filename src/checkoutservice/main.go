package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "./genproto"
	"google.golang.org/grpc"
)

const (
	listenPort = "5050"
)

type checkoutService struct {
	productCatalogSvcAddr string
	cartSvcAddr           string
	currencySvcAddr       string
	shippingSvcAddr       string
	emailSvcAddr          string
	paymentSvcAddr        string
}

func main() {
	port := listenPort
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}

	svc := new(checkoutService)
	mustMapEnv(&svc.shippingSvcAddr, "SHIPPING_SERVICE_ADDR")
	// mustMapEnv(&svc.productCatalogSvcAddr, "PRODUCT_CATALOG_SERVICE_ADDR")
	// mustMapEnv(&svc.cartSvcAddr, "CART_SERVICE_ADDR")
	// mustMapEnv(&svc.currencySvcAddr, "CURRENCY_SERVICE_ADDR")
	// mustMapEnv(&svc.emailSvcAddr, "EMAIL_SERVICE_ADDR")
	// mustMapEnv(&svc.paymentSvcAddr, "PAYMENT_SERVICE_ADDR")

	log.Printf("service config: %+v", svc)

	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		log.Fatal(err)
	}
	srv := grpc.NewServer()
	pb.RegisterCheckoutServiceServer(srv, svc)
	log.Printf("starting to listen on tcp: %q", lis.Addr().String())
	log.Fatal(srv.Serve(lis))
}

func mustMapEnv(target *string, envKey string) {
	v := os.Getenv(envKey)
	if v == "" {
		panic(fmt.Sprintf("environment variable %q not set", envKey))
	}
	*target = v
}

func (cs *checkoutService) CreateOrder(ctx context.Context, req *pb.CreateOrderRequest) (*pb.CreateOrderResponse, error) {
	log.Printf("[CreateOrder] user_id=%q user_currency=%q", req.UserId, req.UserCurrency)
	resp := new(pb.CreateOrderResponse)
	conn, err := grpc.Dial(cs.shippingSvcAddr, grpc.WithInsecure())
	if err != nil {
		return nil, status.Errorf(codes.Unavailable, "could not connect shippping service: %+v", err)
	}
	defer conn.Close()

	shippingQuote, err := pb.NewShippingServiceClient(conn).
		GetQuote(ctx, &pb.GetQuoteRequest{
			Address: req.Address,
			Items:   nil}) // TODO(ahmetb): query CartService for items
	if err != nil {
		return nil, status.Errorf(codes.Unavailable, "failed to get shipping quote: %+v", err)
	}
	resp.ShippingCost = &pb.Money{
		Amount:       shippingQuote.GetCostUsd(),
		CurrencyCode: "USD", // TOD(ahmetb) convert to req.UserCurrency
	}
	// TODO(ahmetb) calculate resp.OrderItem with req.UserCurrency

	return resp, nil
}

func (cs *checkoutService) PlaceOrder(ctx context.Context, req *pb.PlaceOrderRequest) (*pb.PlaceOrderResponse, error) {
	log.Printf("[PlaceOrder] user_id=%q user_currency=%q", req.UserId, req.UserCurrency)
	resp := new(pb.PlaceOrderResponse)
	return resp, nil
}
