// Copyright 2026 Google LLC
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
	"context"
	"net"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
	"google.golang.org/grpc/test/bufconn"
)

type deadlineCheckingProductCatalogService struct {
	pb.UnimplementedProductCatalogServiceServer
}

func (deadlineCheckingProductCatalogService) ListProducts(ctx context.Context, _ *pb.Empty) (*pb.ListProductsResponse, error) {
	deadline, ok := ctx.Deadline()
	if !ok {
		return nil, status.Error(codes.InvalidArgument, "product catalog request context has no deadline")
	}
	if remaining := time.Until(deadline); remaining <= 0 || remaining > 3*time.Second {
		return nil, status.Errorf(codes.InvalidArgument, "product catalog request timeout = %v, want at most %v", remaining, 3*time.Second)
	}
	return &pb.ListProductsResponse{}, nil
}

type unavailableProductCatalogService struct {
	pb.UnimplementedProductCatalogServiceServer
}

func (unavailableProductCatalogService) ListProducts(context.Context, *pb.Empty) (*pb.ListProductsResponse, error) {
	return nil, status.Error(codes.Unavailable, "product catalog unavailable")
}

type availableCurrencyService struct {
	pb.UnimplementedCurrencyServiceServer
}

func (availableCurrencyService) GetSupportedCurrencies(context.Context, *pb.Empty) (*pb.GetSupportedCurrenciesResponse, error) {
	return &pb.GetSupportedCurrenciesResponse{CurrencyCodes: []string{defaultCurrency}}, nil
}

func newTestGRPCConn(t *testing.T, registerServices func(*grpc.Server)) *grpc.ClientConn {
	t.Helper()

	listener := bufconn.Listen(1024 * 1024)
	server := grpc.NewServer()
	registerServices(server)
	go func() {
		_ = server.Serve(listener)
	}()
	t.Cleanup(server.Stop)

	conn, err := grpc.NewClient(
		"passthrough:///test",
		grpc.WithContextDialer(func(context.Context, string) (net.Conn, error) {
			return listener.Dial()
		}),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		t.Fatalf("grpc.NewClient() error = %v", err)
	}
	t.Cleanup(func() { _ = conn.Close() })
	return conn
}

func TestGetProductsHasBoundedTimeout(t *testing.T) {
	conn := newTestGRPCConn(t, func(server *grpc.Server) {
		pb.RegisterProductCatalogServiceServer(server, deadlineCheckingProductCatalogService{})
	})

	fe := &frontendServer{productCatalogSvcConn: conn}
	if _, err := fe.getProducts(context.Background()); err != nil {
		t.Fatalf("getProducts() error = %v", err)
	}
}

func TestHomeReturnsServiceUnavailableWhenProductCatalogFails(t *testing.T) {
	conn := newTestGRPCConn(t, func(server *grpc.Server) {
		pb.RegisterCurrencyServiceServer(server, availableCurrencyService{})
		pb.RegisterProductCatalogServiceServer(server, unavailableProductCatalogService{})
	})

	fe := &frontendServer{
		currencySvcConn:       conn,
		productCatalogSvcConn: conn,
	}
	request := httptest.NewRequest(http.MethodGet, "/", nil)
	request = request.WithContext(context.WithValue(request.Context(), ctxKeyLog{}, logrus.New()))
	response := httptest.NewRecorder()

	fe.homeHandler(response, request)

	if response.Code != http.StatusServiceUnavailable {
		t.Fatalf("homeHandler() status = %d, want %d", response.Code, http.StatusServiceUnavailable)
	}
}
