// Copyright 2018 Google LLC
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
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"time"

	"cloud.google.com/go/profiler"
	"github.com/google/uuid"
	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice/genproto"
	money "github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice/money"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"

	"go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

const (
	listenPort  = "5050"
	usdCurrency = "USD"
)

var log *logrus.Logger

func init() {
	log = logrus.New()
	log.Level = logrus.DebugLevel
	log.Formatter = &logrus.JSONFormatter{
		FieldMap: logrus.FieldMap{
			logrus.FieldKeyTime:  "timestamp",
			logrus.FieldKeyLevel: "severity",
			logrus.FieldKeyMsg:   "message",
		},
		TimestampFormat: time.RFC3339Nano,
	}
	log.Out = os.Stdout
}

type checkoutService struct {
	pb.UnimplementedCheckoutServiceServer

	productCatalogSvcAddr string
	productCatalogSvcConn *grpc.ClientConn

	cartSvcAddr string
	cartSvcConn *grpc.ClientConn

	currencySvcAddr string
	currencySvcConn *grpc.ClientConn

	shippingSvcAddr string
	shippingSvcConn *grpc.ClientConn

	emailSvcAddr string
	emailSvcConn *grpc.ClientConn

	paymentSvcAddr string
	paymentSvcConn *grpc.ClientConn

	// HTTP client for REST multicloud services
	httpClient *http.Client

	// Multicloud service URLs
	awsAccountingURL    string
	azureAnalyticsURL   string
	gcpCrmURL           string
	gcpInventoryURL     string
	gcpFurnitureURL     string
	gcpFoodURL          string
	gcpAccountingURL    string
}

func main() {
	ctx := context.Background()
	if os.Getenv("ENABLE_TRACING") == "1" {
		log.Info("Tracing enabled.")
		initTracing()

	} else {
		log.Info("Tracing disabled.")
	}

	if os.Getenv("ENABLE_PROFILER") == "1" {
		log.Info("Profiling enabled.")
		go initProfiling("checkoutservice", "1.0.0")
	} else {
		log.Info("Profiling disabled.")
	}

	port := listenPort
	if os.Getenv("PORT") != "" {
		port = os.Getenv("PORT")
	}

	svc := new(checkoutService)
	mustMapEnv(&svc.shippingSvcAddr, "SHIPPING_SERVICE_ADDR")
	mustMapEnv(&svc.productCatalogSvcAddr, "PRODUCT_CATALOG_SERVICE_ADDR")
	mustMapEnv(&svc.cartSvcAddr, "CART_SERVICE_ADDR")
	mustMapEnv(&svc.currencySvcAddr, "CURRENCY_SERVICE_ADDR")
	mustMapEnv(&svc.emailSvcAddr, "EMAIL_SERVICE_ADDR")
	mustMapEnv(&svc.paymentSvcAddr, "PAYMENT_SERVICE_ADDR")

	mustConnGRPC(ctx, &svc.shippingSvcConn, svc.shippingSvcAddr)
	mustConnGRPC(ctx, &svc.productCatalogSvcConn, svc.productCatalogSvcAddr)
	mustConnGRPC(ctx, &svc.cartSvcConn, svc.cartSvcAddr)
	mustConnGRPC(ctx, &svc.currencySvcConn, svc.currencySvcAddr)
	mustConnGRPC(ctx, &svc.emailSvcConn, svc.emailSvcAddr)
	mustConnGRPC(ctx, &svc.paymentSvcConn, svc.paymentSvcAddr)

	// Initialize HTTP client with timeout for multicloud services
	svc.httpClient = &http.Client{
		Timeout: 10 * time.Second,
	}

	// Map multicloud service URLs (optional, with defaults)
	svc.awsAccountingURL = os.Getenv("AWS_ACCOUNTING_URL")
	svc.azureAnalyticsURL = os.Getenv("AZURE_ANALYTICS_URL")
	svc.gcpCrmURL = os.Getenv("GCP_CRM_URL")
	svc.gcpInventoryURL = os.Getenv("GCP_INVENTORY_URL")
	svc.gcpFurnitureURL = os.Getenv("GCP_FURNITURE_URL")
	svc.gcpFoodURL = os.Getenv("GCP_FOOD_URL")
	svc.gcpAccountingURL = os.Getenv("GCP_ACCOUNTING_URL")
	
	log.Infof("Multicloud services configured: awsAccounting=%q azureAnalytics=%q gcpCrm=%q gcpInventory=%q gcpFurniture=%q gcpFood=%q gcpAccounting=%q",
		svc.awsAccountingURL, svc.azureAnalyticsURL, svc.gcpCrmURL, svc.gcpInventoryURL, svc.gcpFurnitureURL, svc.gcpFoodURL, svc.gcpAccountingURL)

	log.Infof("service config: %+v", svc)

	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		log.Fatal(err)
	}

	var srv *grpc.Server

	// Propagate trace context always
	otel.SetTextMapPropagator(
		propagation.NewCompositeTextMapPropagator(
			propagation.TraceContext{}, propagation.Baggage{}))
	srv = grpc.NewServer(
		grpc.UnaryInterceptor(otelgrpc.UnaryServerInterceptor()),
		grpc.StreamInterceptor(otelgrpc.StreamServerInterceptor()),
	)

	pb.RegisterCheckoutServiceServer(srv, svc)
	healthpb.RegisterHealthServer(srv, svc)
	log.Infof("starting to listen on tcp: %q", lis.Addr().String())
	err = srv.Serve(lis)
	log.Fatal(err)
}

func initStats() {
	//TODO(arbrown) Implement OpenTelemetry stats
}

func initTracing() {
	var (
		collectorAddr string
		collectorConn *grpc.ClientConn
	)

	ctx := context.Background()
	ctx, cancel := context.WithTimeout(ctx, time.Second*3)
	defer cancel()

	mustMapEnv(&collectorAddr, "COLLECTOR_SERVICE_ADDR")
	mustConnGRPC(ctx, &collectorConn, collectorAddr)

	exporter, err := otlptracegrpc.New(
		ctx,
		otlptracegrpc.WithGRPCConn(collectorConn))
	if err != nil {
		log.Warnf("warn: Failed to create trace exporter: %v", err)
	}
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithSampler(sdktrace.AlwaysSample()))
	otel.SetTracerProvider(tp)

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
			log.Warnf("failed to start profiler: %+v", err)
		} else {
			log.Info("started Stackdriver profiler")
			return
		}
		d := time.Second * 10 * time.Duration(i)
		log.Infof("sleeping %v to retry initializing Stackdriver profiler", d)
		time.Sleep(d)
	}
	log.Warn("could not initialize Stackdriver profiler after retrying, giving up")
}

func mustMapEnv(target *string, envKey string) {
	v := os.Getenv(envKey)
	if v == "" {
		panic(fmt.Sprintf("environment variable %q not set", envKey))
	}
	*target = v
}

func mustConnGRPC(ctx context.Context, conn **grpc.ClientConn, addr string) {
	var err error
	ctx, cancel := context.WithTimeout(ctx, time.Second*3)
	defer cancel()
	*conn, err = grpc.DialContext(ctx, addr,
		grpc.WithInsecure(),
		grpc.WithUnaryInterceptor(otelgrpc.UnaryClientInterceptor()),
		grpc.WithStreamInterceptor(otelgrpc.StreamClientInterceptor()))
	if err != nil {
		panic(errors.Wrapf(err, "grpc: failed to connect %s", addr))
	}
}

func (cs *checkoutService) Check(ctx context.Context, req *healthpb.HealthCheckRequest) (*healthpb.HealthCheckResponse, error) {
	return &healthpb.HealthCheckResponse{Status: healthpb.HealthCheckResponse_SERVING}, nil
}

func (cs *checkoutService) Watch(req *healthpb.HealthCheckRequest, ws healthpb.Health_WatchServer) error {
	return status.Errorf(codes.Unimplemented, "health check via Watch not implemented")
}

func (cs *checkoutService) PlaceOrder(ctx context.Context, req *pb.PlaceOrderRequest) (*pb.PlaceOrderResponse, error) {
	log.Infof("[PlaceOrder] user_id=%q user_currency=%q", req.UserId, req.UserCurrency)

	startTime := time.Now()
	var success bool
	defer func() {
		// Record metrics at the end of the request
		duration := time.Since(startTime)
		_ = cs.recordMetrics(context.Background(), duration, success)
	}()

	orderID, err := uuid.NewUUID()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to generate order uuid")
	}

	prep, err := cs.prepareOrderItemsAndShippingQuoteFromCart(ctx, req.UserId, req.UserCurrency, req.Address)
	if err != nil {
		return nil, status.Errorf(codes.Internal, err.Error())
	}

	// Check inventory before proceeding
	if err := cs.checkInventory(ctx, prep.cartItems); err != nil {
		log.Warnf("Inventory check failed: %v", err)
		// Don't fail the order, just log
	}

	// Check furniture service
	if err := cs.checkFurniture(ctx); err != nil {
		log.Warnf("Furniture check failed: %v", err)
		// Don't fail the order, just log
	}

	// Check food service
	if err := cs.checkFood(ctx); err != nil {
		log.Warnf("Food service check failed: %v", err)
		// Don't fail the order, just log
	}

	// Check accounting service
	if err := cs.checkAccounting(ctx, prep.cartItems); err != nil {
		log.Warnf("Accounting service check failed: %v", err)
		// Don't fail the order, just log
	}

	total := pb.Money{CurrencyCode: req.UserCurrency,
		Units: 0,
		Nanos: 0}
	total = money.Must(money.Sum(total, *prep.shippingCostLocalized))
	for _, it := range prep.orderItems {
		multPrice := money.MultiplySlow(*it.Cost, uint32(it.GetItem().GetQuantity()))
		total = money.Must(money.Sum(total, multPrice))
	}

	txID, err := cs.chargeCard(ctx, &total, req.CreditCard)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to charge card: %+v", err)
	}
	log.Infof("payment went through (transaction_id: %s)", txID)

	// Process transaction in accounting system
	if err := cs.processTransaction(ctx, prep.orderItems); err != nil {
		log.Warnf("Failed to record transaction in accounting system: %v", err)
		// Don't fail the order, just log
	}

	// Manage customer in CRM
	if err := cs.manageCustomer(ctx, req.Email, req.Address); err != nil {
		log.Warnf("Failed to update CRM: %v", err)
		// Don't fail the order, just log
	}

	shippingTrackingID, err := cs.shipOrder(ctx, req.Address, prep.cartItems)
	if err != nil {
		return nil, status.Errorf(codes.Unavailable, "shipping error: %+v", err)
	}

	_ = cs.emptyUserCart(ctx, req.UserId)

	orderResult := &pb.OrderResult{
		OrderId:            orderID.String(),
		ShippingTrackingId: shippingTrackingID,
		ShippingCost:       prep.shippingCostLocalized,
		ShippingAddress:    req.Address,
		Items:              prep.orderItems,
	}

	if err := cs.sendOrderConfirmation(ctx, req.Email, orderResult); err != nil {
		log.Warnf("failed to send order confirmation to %q: %+v", req.Email, err)
	} else {
		log.Infof("order confirmation email sent to %q", req.Email)
	}

	success = true
	resp := &pb.PlaceOrderResponse{Order: orderResult}
	return resp, nil
}

type orderPrep struct {
	orderItems            []*pb.OrderItem
	cartItems             []*pb.CartItem
	shippingCostLocalized *pb.Money
}

func (cs *checkoutService) prepareOrderItemsAndShippingQuoteFromCart(ctx context.Context, userID, userCurrency string, address *pb.Address) (orderPrep, error) {
	var out orderPrep
	cartItems, err := cs.getUserCart(ctx, userID)
	if err != nil {
		return out, fmt.Errorf("cart failure: %+v", err)
	}
	orderItems, err := cs.prepOrderItems(ctx, cartItems, userCurrency)
	if err != nil {
		return out, fmt.Errorf("failed to prepare order: %+v", err)
	}
	shippingUSD, err := cs.quoteShipping(ctx, address, cartItems)
	if err != nil {
		return out, fmt.Errorf("shipping quote failure: %+v", err)
	}
	shippingPrice, err := cs.convertCurrency(ctx, shippingUSD, userCurrency)
	if err != nil {
		return out, fmt.Errorf("failed to convert shipping cost to currency: %+v", err)
	}

	out.shippingCostLocalized = shippingPrice
	out.cartItems = cartItems
	out.orderItems = orderItems
	return out, nil
}

func (cs *checkoutService) quoteShipping(ctx context.Context, address *pb.Address, items []*pb.CartItem) (*pb.Money, error) {
	shippingQuote, err := pb.NewShippingServiceClient(cs.shippingSvcConn).
		GetQuote(ctx, &pb.GetQuoteRequest{
			Address: address,
			Items:   items})
	if err != nil {
		return nil, fmt.Errorf("failed to get shipping quote: %+v", err)
	}
	return shippingQuote.GetCostUsd(), nil
}

func (cs *checkoutService) getUserCart(ctx context.Context, userID string) ([]*pb.CartItem, error) {
	cart, err := pb.NewCartServiceClient(cs.cartSvcConn).GetCart(ctx, &pb.GetCartRequest{UserId: userID})
	if err != nil {
		return nil, fmt.Errorf("failed to get user cart during checkout: %+v", err)
	}
	return cart.GetItems(), nil
}

func (cs *checkoutService) emptyUserCart(ctx context.Context, userID string) error {
	if _, err := pb.NewCartServiceClient(cs.cartSvcConn).EmptyCart(ctx, &pb.EmptyCartRequest{UserId: userID}); err != nil {
		return fmt.Errorf("failed to empty user cart during checkout: %+v", err)
	}
	return nil
}

func (cs *checkoutService) prepOrderItems(ctx context.Context, items []*pb.CartItem, userCurrency string) ([]*pb.OrderItem, error) {
	out := make([]*pb.OrderItem, len(items))
	cl := pb.NewProductCatalogServiceClient(cs.productCatalogSvcConn)

	for i, item := range items {
		product, err := cl.GetProduct(ctx, &pb.GetProductRequest{Id: item.GetProductId()})
		if err != nil {
			return nil, fmt.Errorf("failed to get product #%q", item.GetProductId())
		}
		price, err := cs.convertCurrency(ctx, product.GetPriceUsd(), userCurrency)
		if err != nil {
			return nil, fmt.Errorf("failed to convert price of %q to %s", item.GetProductId(), userCurrency)
		}
		out[i] = &pb.OrderItem{
			Item: item,
			Cost: price}
	}
	return out, nil
}

func (cs *checkoutService) convertCurrency(ctx context.Context, from *pb.Money, toCurrency string) (*pb.Money, error) {
	result, err := pb.NewCurrencyServiceClient(cs.currencySvcConn).Convert(context.TODO(), &pb.CurrencyConversionRequest{
		From:   from,
		ToCode: toCurrency})
	if err != nil {
		return nil, fmt.Errorf("failed to convert currency: %+v", err)
	}
	return result, err
}

func (cs *checkoutService) chargeCard(ctx context.Context, amount *pb.Money, paymentInfo *pb.CreditCardInfo) (string, error) {
	paymentResp, err := pb.NewPaymentServiceClient(cs.paymentSvcConn).Charge(ctx, &pb.ChargeRequest{
		Amount:     amount,
		CreditCard: paymentInfo})
	if err != nil {
		return "", fmt.Errorf("could not charge the card: %+v", err)
	}
	return paymentResp.GetTransactionId(), nil
}

func (cs *checkoutService) sendOrderConfirmation(ctx context.Context, email string, order *pb.OrderResult) error {
	_, err := pb.NewEmailServiceClient(cs.emailSvcConn).SendOrderConfirmation(ctx, &pb.SendOrderConfirmationRequest{
		Email: email,
		Order: order})
	return err
}

func (cs *checkoutService) shipOrder(ctx context.Context, address *pb.Address, items []*pb.CartItem) (string, error) {
	resp, err := pb.NewShippingServiceClient(cs.shippingSvcConn).ShipOrder(ctx, &pb.ShipOrderRequest{
		Address: address,
		Items:   items})
	if err != nil {
		return "", fmt.Errorf("shipment failed: %+v", err)
	}
	return resp.GetTrackingId(), nil
}

// processTransaction calls AWS Accounting Service
func (cs *checkoutService) processTransaction(ctx context.Context, items []*pb.OrderItem) error {
	if cs.awsAccountingURL == "" {
		log.Debug("AWS Accounting URL not configured, skipping")
		return nil
	}

	// Calculate total amount from items
	var totalAmount float64
	for _, item := range items {
		price := float64(item.Cost.Units) + float64(item.Cost.Nanos)/1e9
		totalAmount += price * float64(item.Item.Quantity)
	}

	transactionData := map[string]interface{}{
		"item":  "Online Purchase",
		"price": totalAmount,
		"date":  time.Now().Format("2006-01-02"),
	}

	log.Infof("Recording transaction in AWS Accounting: amount=%.2f", totalAmount)
	return cs.postJSON(ctx, cs.awsAccountingURL+"/transactions", transactionData)
}

// recordMetrics calls Azure Analytics Service
func (cs *checkoutService) recordMetrics(ctx context.Context, duration time.Duration, success bool) error {
	if cs.azureAnalyticsURL == "" {
		log.Debug("Azure Analytics URL not configured, skipping")
		return nil
	}

	metricData := map[string]interface{}{
		"transactionType": "checkout",
		"durationMs":      duration.Milliseconds(),
		"success":         success,
	}

	log.Infof("Recording metrics in Azure Analytics: duration=%v success=%v", duration, success)
	return cs.postJSON(ctx, cs.azureAnalyticsURL+"/metrics", metricData)
}

// manageCustomer calls GCP CRM Service
func (cs *checkoutService) manageCustomer(ctx context.Context, email string, address *pb.Address) error {
	if cs.gcpCrmURL == "" {
		log.Debug("GCP CRM URL not configured, skipping")
		return nil
	}

	// Extract name from email or use address info
	name := "Customer"
	if len(email) > 0 {
		name = email
	}
	surname := "User"
	if address != nil && address.StreetAddress != "" {
		surname = "Customer"
	}

	customerData := map[string]interface{}{
		"name":    name,
		"surname": surname,
	}

	log.Infof("Managing customer in GCP CRM: email=%s", email)
	return cs.postJSON(ctx, cs.gcpCrmURL+"/customers", customerData)
}

// checkInventory calls GCP Inventory Service via PSC
func (cs *checkoutService) checkInventory(ctx context.Context, items []*pb.CartItem) error {
	if cs.gcpInventoryURL == "" {
		log.Debug("GCP Inventory URL not configured, skipping")
		return nil
	}

	// GET inventory status
	_, err := cs.getJSON(ctx, cs.gcpInventoryURL+"/inventory")
	if err != nil {
		log.Warnf("Failed to check inventory: %v", err)
		return err
	}

	log.Infof("Checked inventory for %d items", len(items))
	// Optionally POST inventory updates for each item
	for _, item := range items {
		inventoryData := map[string]interface{}{
			"name": "item",
			"code": item.ProductId,
		}
		if err := cs.postJSON(ctx, cs.gcpInventoryURL+"/inventory", inventoryData); err != nil {
			log.Warnf("Failed to update inventory for %s: %v", item.ProductId, err)
		}
	}

	return nil
}

// checkFurniture calls GCP Furniture Service via HA VPN
func (cs *checkoutService) checkFurniture(ctx context.Context) error {
	if cs.gcpFurnitureURL == "" {
		log.Debug("GCP Furniture URL not configured, skipping")
		return nil
	}

	// GET furniture list
	_, err := cs.getJSON(ctx, cs.gcpFurnitureURL+"/furniture")
	if err != nil {
		log.Warnf("Failed to check furniture: %v", err)
		return err
	}

	// POST sample furniture item
	furnitureData := map[string]interface{}{
		"name":  "sofa",
		"brand": "ikea",
	}

	log.Infof("Checking furniture service")
	return cs.postJSON(ctx, cs.gcpFurnitureURL+"/furniture", furnitureData)
}

// checkFood calls GCP Food Service on Cloud Run (which internally calls Inventory Service)
func (cs *checkoutService) checkFood(ctx context.Context) error {
	if cs.gcpFoodURL == "" {
		log.Debug("GCP Food URL not configured, skipping")
		return nil
	}

	// GET food list - this will trigger the food service to call inventory service
	foodData, err := cs.getJSON(ctx, cs.gcpFoodURL+"/food")
	if err != nil {
		log.Warnf("Failed to check food service: %v", err)
		return err
	}

	log.Infof("Successfully checked food service, received data: %v", foodData)
	
	// Optionally POST a new food item
	newFood := map[string]interface{}{
		"name":      "Caesar Salad",
		"category":  "Salad",
		"price":     8.99,
		"available": true,
	}

	if err := cs.postJSON(ctx, cs.gcpFoodURL+"/food", newFood); err != nil {
		log.Warnf("Failed to add food item: %v", err)
		// Don't return error, just log
	}

	log.Infof("Food service check completed successfully")
	return nil
}

// checkAccounting calls GCP Accounting Service via VPC Connector (which internally calls CRM Service)
func (cs *checkoutService) checkAccounting(ctx context.Context, items []*pb.CartItem) error {
	if cs.gcpAccountingURL == "" {
		log.Debug("GCP Accounting URL not configured, skipping")
		return nil
	}

	// GET transactions list - this will trigger the accounting service to call CRM service
	accountingData, err := cs.getJSON(ctx, cs.gcpAccountingURL+"/transactions")
	if err != nil {
		log.Warnf("Failed to check accounting service: %v", err)
		return err
	}

	log.Infof("Successfully checked accounting service, received data: %v", accountingData)
	
	// Optionally POST a new transaction for this order
	// Calculate total price from cart items
	var totalPrice float64
	for _, item := range items {
		// Assuming we have product info, otherwise use a placeholder
		totalPrice += 10.00 // Placeholder price per item
	}

	newTransaction := map[string]interface{}{
		"item":     "Online Order",
		"price":    totalPrice,
		"date":     "2025-10-29",
		"customer": "Online Customer",
	}

	if err := cs.postJSON(ctx, cs.gcpAccountingURL+"/transactions", newTransaction); err != nil {
		log.Warnf("Failed to add transaction to accounting: %v", err)
		// Don't return error, just log
	}

	log.Infof("Accounting service check completed successfully")
	return nil
}

// Helper method to POST JSON
func (cs *checkoutService) postJSON(ctx context.Context, url string, data map[string]interface{}) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("failed to marshal JSON: %v", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := cs.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	log.Debugf("POST %s succeeded with status %d", url, resp.StatusCode)
	return nil
}

// Helper method to GET JSON
func (cs *checkoutService) getJSON(ctx context.Context, url string) (map[string]interface{}, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	resp, err := cs.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %v", err)
	}

	log.Debugf("GET %s succeeded with status %d", url, resp.StatusCode)
	return result, nil
}
