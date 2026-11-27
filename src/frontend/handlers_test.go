package main

import (
	"context"
	"html"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"sync"
	"testing"

	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
	"google.golang.org/grpc/test/bufconn"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"
)

const bufSize = 1024 * 1024

// stubProductCatalogServer simula ProductCatalogService en memoria.
type stubProductCatalogServer struct {
	pb.UnimplementedProductCatalogServiceServer
	mu            sync.Mutex
	product       *pb.Product
	err           error
	callCount     int
	lastProductID string
}

func (s *stubProductCatalogServer) GetProduct(_ context.Context, req *pb.GetProductRequest) (*pb.Product, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.callCount++
	s.lastProductID = req.GetId()
	if s.err != nil {
		return nil, s.err
	}
	return s.product, nil
}

// mockCartServer simula y espía las invocaciones a CartService en memoria.
type mockCartServer struct {
	pb.UnimplementedCartServiceServer
	mu        sync.Mutex
	err       error
	callCount int
	lastReq   *pb.AddItemRequest
}

func (m *mockCartServer) AddItem(_ context.Context, req *pb.AddItemRequest) (*pb.Empty, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.callCount++
	m.lastReq = req
	if m.err != nil {
		return nil, m.err
	}
	return &pb.Empty{}, nil
}

// setupIsolatedFrontend levanta servidores gRPC en memoria (bufconn) sin red ni Docker.
func setupIsolatedFrontend(t *testing.T, catalogStub *stubProductCatalogServer, cartMock *mockCartServer) *frontendServer {
	t.Helper()

	catalogLis := bufconn.Listen(bufSize)
	catalogSrv := grpc.NewServer()
	pb.RegisterProductCatalogServiceServer(catalogSrv, catalogStub)
	go func() { _ = catalogSrv.Serve(catalogLis) }()

	catalogConn, err := grpc.NewClient(
		"passthrough:///bufnet",
		grpc.WithContextDialer(func(ctx context.Context, _ string) (net.Conn, error) {
			return catalogLis.DialContext(ctx)
		}),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		t.Fatalf("failed to create bufconn client for catalog: %v", err)
	}

	cartLis := bufconn.Listen(bufSize)
	cartSrv := grpc.NewServer()
	pb.RegisterCartServiceServer(cartSrv, cartMock)
	go func() { _ = cartSrv.Serve(cartLis) }()

	cartConn, err := grpc.NewClient(
		"passthrough:///bufnet",
		grpc.WithContextDialer(func(ctx context.Context, _ string) (net.Conn, error) {
			return cartLis.DialContext(ctx)
		}),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		t.Fatalf("failed to create bufconn client for cart: %v", err)
	}

	t.Cleanup(func() {
		_ = catalogConn.Close()
		catalogSrv.Stop()
		_ = catalogLis.Close()

		_ = cartConn.Close()
		cartSrv.Stop()
		_ = cartLis.Close()
	})

	return &frontendServer{
		productCatalogSvcConn: catalogConn,
		cartSvcConn:           cartConn,
	}
}

func newAddToCartRequest(form url.Values, sessionID string, includeSession bool, cookies ...*http.Cookie) *http.Request {
	req := httptest.NewRequest(http.MethodPost, "/cart", strings.NewReader(form.Encode()))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	logger := logrus.New()
	logger.SetOutput(io.Discard)

	ctx := context.WithValue(req.Context(), ctxKeyLog{}, logger)
	if includeSession {
		ctx = context.WithValue(ctx, ctxKeySessionID{}, sessionID)
	}
	for _, c := range cookies {
		req.AddCookie(c)
	}
	return req.WithContext(ctx)
}

func TestAddToCartHandler(t *testing.T) {
	t.Run("[TC-API-01] Insercion nominal valida con producto existente", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z", Name: "Sunglasses"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"OLJCESPC7Z"}, "quantity": {"2"}}
		req := newAddToCartRequest(form, "sess-test-01", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusFound {
			t.Fatalf("expected status %d, got %d", http.StatusFound, rec.Code)
		}
		if loc := rec.Header().Get("Location"); loc != baseUrl+"/cart" {
			t.Errorf("expected Location %q, got %q", baseUrl+"/cart", loc)
		}
		if catalog.callCount != 1 || catalog.lastProductID != "OLJCESPC7Z" {
			t.Errorf("expected 1 GetProduct call for OLJCESPC7Z, got count=%d id=%q", catalog.callCount, catalog.lastProductID)
		}
		if cart.callCount != 1 {
			t.Fatalf("expected 1 AddItem call, got %d", cart.callCount)
		}
		if cart.lastReq.GetUserId() != "sess-test-01" ||
			cart.lastReq.GetItem().GetProductId() != "OLJCESPC7Z" ||
			cart.lastReq.GetItem().GetQuantity() != 2 {
			t.Errorf("unexpected AddItem payload: %+v", cart.lastReq)
		}
	})

	t.Run("[TC-API-02] Limite inferior valido de cantidad (quantity = 1)", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"OLJCESPC7Z"}, "quantity": {"1"}}
		req := newAddToCartRequest(form, "sess-test-02", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusFound {
			t.Fatalf("expected status %d, got %d", http.StatusFound, rec.Code)
		}
		if cart.callCount != 1 || cart.lastReq.GetItem().GetQuantity() != 1 {
			t.Errorf("expected AddItem with Quantity=1, got count=%d req=%+v", cart.callCount, cart.lastReq)
		}
	})

	t.Run("[TC-API-03] Limite superior valido de cantidad (quantity = 10)", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"OLJCESPC7Z"}, "quantity": {"10"}}
		req := newAddToCartRequest(form, "sess-test-03", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusFound {
			t.Fatalf("expected status %d, got %d", http.StatusFound, rec.Code)
		}
		if cart.callCount != 1 || cart.lastReq.GetItem().GetQuantity() != 10 {
			t.Errorf("expected AddItem with Quantity=10, got count=%d req=%+v", cart.callCount, cart.lastReq)
		}
	})

	t.Run("[TC-API-04] Limite inferior invalido de cantidad en cero (quantity = 0)", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"OLJCESPC7Z"}, "quantity": {"0"}}
		req := newAddToCartRequest(form, "sess-test-04", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusUnprocessableEntity {
			t.Fatalf("expected status %d, got %d", http.StatusUnprocessableEntity, rec.Code)
		}
		body := html.UnescapeString(rec.Body.String())
		if !strings.Contains(body, "Field 'Quantity' is invalid: required") {
			t.Errorf("expected validation error for Quantity, got body: %s", body)
		}
		if catalog.callCount != 0 || cart.callCount != 0 {
			t.Errorf("expected 0 gRPC calls, got catalog=%d cart=%d", catalog.callCount, cart.callCount)
		}
	})

	t.Run("[TC-API-05] Limite superior invalido de cantidad excedida (quantity = 11)", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"OLJCESPC7Z"}, "quantity": {"11"}}
		req := newAddToCartRequest(form, "sess-test-05", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusUnprocessableEntity {
			t.Fatalf("expected status %d, got %d", http.StatusUnprocessableEntity, rec.Code)
		}
		body := html.UnescapeString(rec.Body.String())
		if !strings.Contains(body, "Field 'Quantity' is invalid: lte") {
			t.Errorf("expected lte validation error for Quantity, got body: %s", body)
		}
		if catalog.callCount != 0 || cart.callCount != 0 {
			t.Errorf("expected 0 gRPC calls, got catalog=%d cart=%d", catalog.callCount, cart.callCount)
		}
	})

	t.Run("[TC-API-06] Particion invalida: cantidad negativa (quantity = -3)", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"OLJCESPC7Z"}, "quantity": {"-3"}}
		req := newAddToCartRequest(form, "sess-test-06", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusUnprocessableEntity {
			t.Fatalf("expected status %d, got %d", http.StatusUnprocessableEntity, rec.Code)
		}
		body := html.UnescapeString(rec.Body.String())
		if !strings.Contains(body, "Field 'Quantity' is invalid: required") {
			t.Errorf("expected validation error for negative Quantity, got body: %s", body)
		}
		if catalog.callCount != 0 || cart.callCount != 0 {
			t.Errorf("expected 0 gRPC calls, got catalog=%d cart=%d", catalog.callCount, cart.callCount)
		}
	})

	t.Run("[TC-API-07] Particion invalida: cantidad no numerica (quantity = abc)", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"OLJCESPC7Z"}, "quantity": {"abc"}}
		req := newAddToCartRequest(form, "sess-test-07", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusUnprocessableEntity {
			t.Fatalf("expected status %d, got %d", http.StatusUnprocessableEntity, rec.Code)
		}
		body := html.UnescapeString(rec.Body.String())
		if !strings.Contains(body, "Field 'Quantity' is invalid: required") {
			t.Errorf("expected validation error for non-numeric Quantity, got body: %s", body)
		}
		if catalog.callCount != 0 || cart.callCount != 0 {
			t.Errorf("expected 0 gRPC calls, got catalog=%d cart=%d", catalog.callCount, cart.callCount)
		}
	})

	t.Run("[TC-API-08] Particion invalida: product_id vacio", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {""}, "quantity": {"2"}}
		req := newAddToCartRequest(form, "sess-test-08", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusUnprocessableEntity {
			t.Fatalf("expected status %d, got %d", http.StatusUnprocessableEntity, rec.Code)
		}
		body := html.UnescapeString(rec.Body.String())
		if !strings.Contains(body, "Field 'ProductID' is invalid: required") {
			t.Errorf("expected validation error for ProductID, got body: %s", body)
		}
		if catalog.callCount != 0 || cart.callCount != 0 {
			t.Errorf("expected 0 gRPC calls, got catalog=%d cart=%d", catalog.callCount, cart.callCount)
		}
	})

	t.Run("[TC-API-09] Multiples campos invalidos simultaneamente", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {""}, "quantity": {"15"}}
		req := newAddToCartRequest(form, "sess-test-09", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusUnprocessableEntity {
			t.Fatalf("expected status %d, got %d", http.StatusUnprocessableEntity, rec.Code)
		}
		body := html.UnescapeString(rec.Body.String())
		if !strings.Contains(body, "Field 'Quantity' is invalid: lte") ||
			!strings.Contains(body, "Field 'ProductID' is invalid: required") {
			t.Errorf("expected validation errors for both Quantity and ProductID, got body: %s", body)
		}
		if catalog.callCount != 0 || cart.callCount != 0 {
			t.Errorf("expected 0 gRPC calls, got catalog=%d cart=%d", catalog.callCount, cart.callCount)
		}
	})

	t.Run("[TC-API-10] Producto no encontrado o fallo en ProductCatalogService", func(t *testing.T) {
		catalog := &stubProductCatalogServer{err: status.Error(codes.NotFound, "product not found")}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"UNKNOWN-ID"}, "quantity": {"1"}}
		req := newAddToCartRequest(form, "sess-test-10", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusInternalServerError {
			t.Fatalf("expected status %d, got %d", http.StatusInternalServerError, rec.Code)
		}
		body := html.UnescapeString(rec.Body.String())
		if !strings.Contains(body, "could not retrieve product") {
			t.Errorf("expected error message 'could not retrieve product', got body: %s", body)
		}
		if catalog.callCount != 1 {
			t.Errorf("expected 1 GetProduct call, got %d", catalog.callCount)
		}
		if cart.callCount != 0 {
			t.Errorf("expected 0 AddItem calls when GetProduct fails, got %d", cart.callCount)
		}
	})

	t.Run("[TC-API-11] Fallo de persistencia en CartService.AddItem", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{err: status.Error(codes.Unavailable, "cart service unavailable")}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"OLJCESPC7Z"}, "quantity": {"3"}}
		req := newAddToCartRequest(form, "sess-test-11", true)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusInternalServerError {
			t.Fatalf("expected status %d, got %d", http.StatusInternalServerError, rec.Code)
		}
		body := html.UnescapeString(rec.Body.String())
		if !strings.Contains(body, "failed to add to cart") {
			t.Errorf("expected error message 'failed to add to cart', got body: %s", body)
		}
		if catalog.callCount != 1 || cart.callCount != 1 {
			t.Errorf("expected 1 call to catalog and 1 to cart, got catalog=%d cart=%d", catalog.callCount, cart.callCount)
		}
	})

	t.Run("[TC-API-12] Ausencia de session_id en contexto y preservacion de cookies", func(t *testing.T) {
		catalog := &stubProductCatalogServer{product: &pb.Product{Id: "OLJCESPC7Z"}}
		cart := &mockCartServer{}
		fe := setupIsolatedFrontend(t, catalog, cart)

		form := url.Values{"product_id": {"OLJCESPC7Z"}, "quantity": {"1"}}
		currencyCookie := &http.Cookie{Name: cookieCurrency, Value: "EUR"}
		req := newAddToCartRequest(form, "", false, currencyCookie)
		rec := httptest.NewRecorder()

		fe.addToCartHandler(rec, req)

		if rec.Code != http.StatusFound {
			t.Fatalf("expected status %d, got %d", http.StatusFound, rec.Code)
		}
		if cart.callCount != 1 || cart.lastReq.GetUserId() != "" {
			t.Errorf("expected empty UserId when ctxKeySessionID is absent, got count=%d user=%q", cart.callCount, cart.lastReq.GetUserId())
		}
		if len(rec.Header().Values("Set-Cookie")) != 0 {
			t.Errorf("expected existing cookies not to be overwritten, got Set-Cookie: %v", rec.Header().Values("Set-Cookie"))
		}
	})
}