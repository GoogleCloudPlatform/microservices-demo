package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"google.golang.org/grpc"

	pb "./genproto"
)

const (
	listenPort = "7000"
)

type currencyServer struct {
	currencies      []string
	conversionRates map[[2]string]float64
}

func main() {
	port := listenPort
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}

	svc := &currencyServer{
		currencies: []string{"USD", "EUR", "CAD"},
		conversionRates: map[[2]string]float64{
			{"USD", "EUR"}: 0.86,
			{"EUR", "USD"}: 1 / 0.86,

			{"USD", "CAD"}: 1.33,
			{"CAD", "USD"}: 1 / 1.33,

			{"EUR", "CAD"}: 1.54,
			{"CAD", "EUR"}: 1 / 1.54,
		},
	}

	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		log.Fatal(err)
	}
	srv := grpc.NewServer()
	pb.RegisterCurrencyServiceServer(srv, svc)
	log.Printf("starting to listen on tcp: %q", lis.Addr().String())
	log.Fatal(srv.Serve(lis))
}

func (cs *currencyServer) GetSupportedCurrencies(_ context.Context, _ *pb.Empty) (*pb.GetSupportedCurrenciesResponse, error) {
	log.Printf("requesting supported currencies (%d)", len(cs.currencies))
	return &pb.GetSupportedCurrenciesResponse{CurrencyCodes: cs.currencies}, nil
}

func (cs *currencyServer) Convert(_ context.Context, req *pb.CurrencyConversionRequest) (*pb.Money, error) {
	log.Printf("requesting currency conversion [%+v] --> %s", req.From, req.ToCode)
	conv := [2]string{req.GetFrom().GetCurrencyCode(), req.GetToCode()}
	rate, ok := cs.conversionRates[conv]
	if !ok {
		return nil, status.Errorf(codes.InvalidArgument, "conversion %v not supported", conv)
	}
	if req.From == nil {
		return nil, status.Errorf(codes.InvalidArgument, "no money amount provided")
	}

	amount := convert(*req.From.Amount, rate)
	return &pb.Money{
		CurrencyCode: req.GetToCode(),
		Amount:       &amount}, nil
}
