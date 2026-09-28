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
	"io"
	"net"
	"sync"
	"testing"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
	"google.golang.org/grpc/test/bufconn"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice/genproto"
)

const fakeTrackingID = "AB-123456789-CD"

func init() {
	// Las pruebas no necesitan ver los logs del servicio.
	log.Out = io.Discard
}

// fakeOrderClient es un OrderServiceClient falso que no usa red. Devuelve, en
// orden, los errores de errs; cuando se acaban, responde con éxito.
type fakeOrderClient struct {
	mu    sync.Mutex
	errs  []error
	calls int
	reqs  []*pb.RecordOrderRequest
}

func (f *fakeOrderClient) RecordOrder(ctx context.Context, in *pb.RecordOrderRequest, _ ...grpc.CallOption) (*pb.RecordOrderResponse, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.calls++
	f.reqs = append(f.reqs, in)
	if f.calls <= len(f.errs) {
		return nil, f.errs[f.calls-1]
	}
	return &pb.RecordOrderResponse{OrderId: in.GetOrder().GetOrderId()}, nil
}

func (f *fakeOrderClient) GetOrderByTrackingId(context.Context, *pb.GetOrderByTrackingIdRequest, ...grpc.CallOption) (*pb.TrackedOrder, error) {
	return nil, status.Error(codes.Unimplemented, "not used in these tests")
}

// fastRetries acorta las esperas entre intentos para que las pruebas no tarden.
func fastRetries(t *testing.T) {
	t.Helper()
	prev := recordOrderBackoff
	recordOrderBackoff = []time.Duration{time.Millisecond, 2 * time.Millisecond}
	t.Cleanup(func() { recordOrderBackoff = prev })
}

func sampleOrder() *pb.Order {
	return &pb.Order{
		OrderId:            "order-1",
		ShippingTrackingId: fakeTrackingID,
		PurchasedAtUnix:    time.Now().Unix(),
	}
}

func TestRecordOrder(t *testing.T) {
	unavailable := status.Error(codes.Unavailable, "orderservice down")
	deadline := status.Error(codes.DeadlineExceeded, "too slow")

	tests := []struct {
		name      string
		errs      []error
		wantCalls int
	}{
		{name: "éxito al primer intento", errs: nil, wantCalls: 1},
		{name: "éxito después de un Unavailable", errs: []error{unavailable}, wantCalls: 2},
		{name: "éxito después de un DeadlineExceeded", errs: []error{deadline}, wantCalls: 2},
		{name: "InvalidArgument no se reintenta", errs: []error{status.Error(codes.InvalidArgument, "missing order_id")}, wantCalls: 1},
		{name: "Internal no se reintenta", errs: []error{status.Error(codes.Internal, "redis failed")}, wantCalls: 1},
		{name: "tres fallos seguidos se rinde en el tercero", errs: []error{unavailable, unavailable, unavailable, unavailable}, wantCalls: 3},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			fastRetries(t)
			fake := &fakeOrderClient{errs: tt.errs}
			cs := &checkoutService{orderSvcClient: fake}

			attempts := cs.recordOrder(context.Background(), sampleOrder())

			if fake.calls != tt.wantCalls {
				t.Errorf("RecordOrder calls = %d, want %d", fake.calls, tt.wantCalls)
			}
			if attempts != tt.wantCalls {
				t.Errorf("recordOrder returned %d attempts, want %d", attempts, tt.wantCalls)
			}
		})
	}
}

func TestRecordOrderEachAttemptHasItsOwnTimeout(t *testing.T) {
	fastRetries(t)
	prev := recordOrderAttemptTimeout
	recordOrderAttemptTimeout = 20 * time.Millisecond
	t.Cleanup(func() { recordOrderAttemptTimeout = prev })

	var deadlines []time.Time
	client := &deadlineRecordingClient{onCall: func(ctx context.Context) {
		d, ok := ctx.Deadline()
		if !ok {
			t.Error("RecordOrder was called without a deadline")
		}
		deadlines = append(deadlines, d)
	}}
	cs := &checkoutService{orderSvcClient: client}

	cs.recordOrder(context.Background(), sampleOrder())

	if len(deadlines) != recordOrderMaxAttempts {
		t.Fatalf("got %d attempts, want %d", len(deadlines), recordOrderMaxAttempts)
	}
	if !deadlines[1].After(deadlines[0]) || !deadlines[2].After(deadlines[1]) {
		t.Errorf("each attempt should get a fresh deadline, got %v", deadlines)
	}
}

// deadlineRecordingClient siempre falla con Unavailable y deja ver el
// contexto de cada intento.
type deadlineRecordingClient struct {
	fakeOrderClient
	onCall func(ctx context.Context)
}

func (d *deadlineRecordingClient) RecordOrder(ctx context.Context, _ *pb.RecordOrderRequest, _ ...grpc.CallOption) (*pb.RecordOrderResponse, error) {
	d.onCall(ctx)
	return nil, status.Error(codes.Unavailable, "down")
}

func TestPlaceOrderRecordsOrderWithShippingTrackingID(t *testing.T) {
	fastRetries(t)
	fake := &fakeOrderClient{}
	cs := newTestCheckoutService(t)
	cs.orderSvcClient = fake

	resp, err := cs.PlaceOrder(context.Background(), placeOrderRequest())
	if err != nil {
		t.Fatalf("PlaceOrder returned error: %v", err)
	}

	if fake.calls != 1 {
		t.Fatalf("RecordOrder calls = %d, want 1", fake.calls)
	}
	got := fake.reqs[0].GetOrder()
	if got.GetShippingTrackingId() != fakeTrackingID {
		t.Errorf("recorded tracking id = %q, want %q (from shippingservice)", got.GetShippingTrackingId(), fakeTrackingID)
	}
	if got.GetShippingTrackingId() != resp.GetOrder().GetShippingTrackingId() {
		t.Errorf("recorded tracking id %q differs from the one returned to the customer %q",
			got.GetShippingTrackingId(), resp.GetOrder().GetShippingTrackingId())
	}
	if got.GetOrderId() == "" || got.GetOrderId() != resp.GetOrder().GetOrderId() {
		t.Errorf("recorded order id = %q, want %q", got.GetOrderId(), resp.GetOrder().GetOrderId())
	}
	if got.GetPurchasedAtUnix() == 0 {
		t.Error("purchased_at_unix was not set")
	}
	if len(got.GetItems()) != 1 || got.GetShippingAddress() == nil || got.GetShippingCost() == nil {
		t.Errorf("order is missing items, address or shipping cost: %+v", got)
	}
	// 2 artículos de 10 USD + 5 USD de envío.
	if got.GetTotal().GetUnits() != 25 || got.GetTotal().GetCurrencyCode() != "USD" {
		t.Errorf("total = %+v, want 25 USD", got.GetTotal())
	}
}

func TestPlaceOrderSucceedsWhenRecordOrderFailsThreeTimes(t *testing.T) {
	fastRetries(t)
	down := status.Error(codes.Unavailable, "orderservice down")
	fake := &fakeOrderClient{errs: []error{down, down, down}}
	cs := newTestCheckoutService(t)
	cs.orderSvcClient = fake

	resp, err := cs.PlaceOrder(context.Background(), placeOrderRequest())
	if err != nil {
		t.Fatalf("PlaceOrder must not fail when orderservice is down, got: %v", err)
	}
	if resp.GetOrder().GetShippingTrackingId() != fakeTrackingID {
		t.Errorf("tracking id = %q, want %q", resp.GetOrder().GetShippingTrackingId(), fakeTrackingID)
	}
	if fake.calls != recordOrderMaxAttempts {
		t.Errorf("RecordOrder calls = %d, want %d", fake.calls, recordOrderMaxAttempts)
	}
}

func TestPlaceOrderWithTrackingDisabledMakesNoCall(t *testing.T) {
	t.Setenv("ENABLE_ORDER_TRACKING", "")
	t.Setenv("ORDER_SERVICE_ADDR", "")

	cs := newTestCheckoutService(t)
	// Sin ORDER_SERVICE_ADDR no debe hacer panic ni crear el cliente.
	cs.configureOrderTracking(context.Background())
	if cs.orderSvcClient != nil || cs.orderSvcConn != nil {
		t.Fatal("order service client was created with tracking disabled")
	}

	if _, err := cs.PlaceOrder(context.Background(), placeOrderRequest()); err != nil {
		t.Fatalf("PlaceOrder returned error: %v", err)
	}
	if got := cs.recordOrder(context.Background(), sampleOrder()); got != 0 {
		t.Errorf("recordOrder made %d attempts with tracking disabled, want 0", got)
	}
}

func TestConfigureOrderTrackingOnlyWithTrue(t *testing.T) {
	for _, v := range []string{"", "false", "1", "TRUE"} {
		t.Run(v, func(t *testing.T) {
			t.Setenv("ENABLE_ORDER_TRACKING", v)
			t.Setenv("ORDER_SERVICE_ADDR", "")
			cs := &checkoutService{}
			cs.configureOrderTracking(context.Background())
			if cs.orderSvcClient != nil {
				t.Errorf("ENABLE_ORDER_TRACKING=%q should keep tracking off", v)
			}
		})
	}

	t.Run("true", func(t *testing.T) {
		t.Setenv("ENABLE_ORDER_TRACKING", "true")
		t.Setenv("ORDER_SERVICE_ADDR", "orderservice:7070")
		cs := &checkoutService{}
		cs.configureOrderTracking(context.Background())
		t.Cleanup(func() { cs.orderSvcConn.Close() })
		if cs.orderSvcClient == nil || cs.orderSvcAddr != "orderservice:7070" {
			t.Errorf("tracking should be on: addr=%q client=%v", cs.orderSvcAddr, cs.orderSvcClient)
		}
	})
}

// --- Dependencias falsas de checkoutservice, servidas en memoria con bufconn ---

func placeOrderRequest() *pb.PlaceOrderRequest {
	return &pb.PlaceOrderRequest{
		UserId:       "user-1",
		UserCurrency: "USD",
		Email:        "someone@example.com",
		Address:      &pb.Address{StreetAddress: "1600 Amphitheatre Pkwy", City: "Mountain View", Country: "US", ZipCode: 94043},
		CreditCard:   &pb.CreditCardInfo{CreditCardNumber: "4432-8015-6152-0454", CreditCardCvv: 672, CreditCardExpirationYear: 2039, CreditCardExpirationMonth: 1},
	}
}

// newTestCheckoutService arma un checkoutService cuyas seis dependencias
// (cart, catálogo, moneda, envío, pago y correo) son falsas y viven en memoria.
func newTestCheckoutService(t *testing.T) *checkoutService {
	t.Helper()
	lis := bufconn.Listen(1024 * 1024)
	srv := grpc.NewServer()
	pb.RegisterCartServiceServer(srv, fakeCart{})
	pb.RegisterProductCatalogServiceServer(srv, fakeCatalog{})
	pb.RegisterCurrencyServiceServer(srv, fakeCurrency{})
	pb.RegisterShippingServiceServer(srv, fakeShipping{})
	pb.RegisterPaymentServiceServer(srv, fakePayment{})
	pb.RegisterEmailServiceServer(srv, fakeEmail{})
	go srv.Serve(lis)
	t.Cleanup(srv.Stop)

	conn, err := grpc.NewClient("passthrough:///bufnet",
		grpc.WithContextDialer(func(ctx context.Context, _ string) (net.Conn, error) { return lis.DialContext(ctx) }),
		grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("failed to dial bufconn: %v", err)
	}
	t.Cleanup(func() { conn.Close() })

	return &checkoutService{
		productCatalogSvcConn: conn,
		cartSvcConn:           conn,
		currencySvcConn:       conn,
		shippingSvcConn:       conn,
		emailSvcConn:          conn,
		paymentSvcConn:        conn,
	}
}

type fakeCart struct {
	pb.UnimplementedCartServiceServer
}

func (fakeCart) GetCart(_ context.Context, req *pb.GetCartRequest) (*pb.Cart, error) {
	return &pb.Cart{UserId: req.GetUserId(), Items: []*pb.CartItem{{ProductId: "OLJCESPC7Z", Quantity: 2}}}, nil
}

func (fakeCart) EmptyCart(context.Context, *pb.EmptyCartRequest) (*pb.Empty, error) {
	return &pb.Empty{}, nil
}

type fakeCatalog struct {
	pb.UnimplementedProductCatalogServiceServer
}

func (fakeCatalog) GetProduct(_ context.Context, req *pb.GetProductRequest) (*pb.Product, error) {
	return &pb.Product{Id: req.GetId(), PriceUsd: &pb.Money{CurrencyCode: "USD", Units: 10}}, nil
}

type fakeCurrency struct {
	pb.UnimplementedCurrencyServiceServer
}

func (fakeCurrency) Convert(_ context.Context, req *pb.CurrencyConversionRequest) (*pb.Money, error) {
	return &pb.Money{CurrencyCode: req.GetToCode(), Units: req.GetFrom().GetUnits(), Nanos: req.GetFrom().GetNanos()}, nil
}

type fakeShipping struct {
	pb.UnimplementedShippingServiceServer
}

func (fakeShipping) GetQuote(context.Context, *pb.GetQuoteRequest) (*pb.GetQuoteResponse, error) {
	return &pb.GetQuoteResponse{CostUsd: &pb.Money{CurrencyCode: "USD", Units: 5}}, nil
}

func (fakeShipping) ShipOrder(context.Context, *pb.ShipOrderRequest) (*pb.ShipOrderResponse, error) {
	return &pb.ShipOrderResponse{TrackingId: fakeTrackingID}, nil
}

type fakePayment struct {
	pb.UnimplementedPaymentServiceServer
}

func (fakePayment) Charge(context.Context, *pb.ChargeRequest) (*pb.ChargeResponse, error) {
	return &pb.ChargeResponse{TransactionId: "tx-1"}, nil
}

type fakeEmail struct {
	pb.UnimplementedEmailServiceServer
}

func (fakeEmail) SendOrderConfirmation(context.Context, *pb.SendOrderConfirmationRequest) (*pb.Empty, error) {
	return &pb.Empty{}, nil
}
