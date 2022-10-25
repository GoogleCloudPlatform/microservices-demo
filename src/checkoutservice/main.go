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
	"context"
	"fmt"
	"net"
	"os"
	"time"

	"google.golang.org/grpc/metadata"

	"cloud.google.com/go/profiler"
	"contrib.go.opencensus.io/exporter/jaeger"
	"contrib.go.opencensus.io/exporter/stackdriver"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"go.opencensus.io/plugin/ocgrpc"
	"go.opencensus.io/stats/view"
	"go.opencensus.io/trace"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice/genproto"
	money "github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice/money"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

const (
	listenPort            = "5050"
	usdCurrency           = "USD"
	FRONTEND              = "frontend"
	ADSERVICE             = "adservice"
	CARTSERVICE           = "cartservice"
	CHECKOUTSERVICE       = "checkoutservice"
	CURRENCYSERVICE       = "currencyservice"
	EMAILSERVICE          = "emailservice"
	PAYMENTSERVICE        = "paymentservice"
	PRODUCTCATALOGSERVICE = "productcatalogservice"
	RECOMMENDATIONSERVICE = "recommendationservice"
	SHIPPINGSERVICE       = "shippingservice"
)

// NOTE: logLevel must be a GELF valid severity value (WARN or ERROR), INFO if not specified
func emitLog(event string, logLevel string) {
	timestamp := time.Now().Format("2006-01-02T15:04:05.000Z")

	switch logLevel {
	case "ERROR":
		log.Error(timestamp + " - ERROR - " + CHECKOUTSERVICE + " - " + event)
	case "WARN":
		log.Warn(timestamp + " - WARN - " + CHECKOUTSERVICE + " - " + event)
	default:
		log.Info(timestamp + " - INFO - " + CHECKOUTSERVICE + " - " + event)
	}
}

// Verify gRPC response code and log the corresponding event
func checkResponse(responseCode codes.Code, serviceName string, reqId string, err error) {
	fmt.Println("received code: " + responseCode.String())

	if responseCode == codes.Unavailable || responseCode == codes.DeadlineExceeded {
		event := "Failing to contact " + serviceName + " (request_id: " + reqId + "). Root cause: (" + err.Error() + ")"
		emitLog(event, "ERROR")
	} else if responseCode == codes.OK {
		event := "Receiving answer from " + serviceName + " (request_id: " + reqId + ")"
		emitLog(event, "INFO")
	} else {
		event := "Error response received from " + serviceName + " (request_id: " + reqId + ")"
		emitLog(event, "ERROR")
	}
}

func readMetadata(ctx context.Context) (string, string) {
	md, _ := metadata.FromIncomingContext(ctx)
	reqId := md.Get("requestid")
	invService := md.Get("servicename")
	var RequestID, ServiceName string

	if len(reqId) > 0 && len(invService) > 0 {
		RequestID = reqId[0]
		ServiceName = invService[0]
		emitLog("Received request from "+ServiceName+" (request_id: "+RequestID+")", "INFO")

	} else {
		emitLog(CHECKOUTSERVICE+": An error occurred while retrieving the RequestID", "ERROR")
	}

	return RequestID, ServiceName
}

func setMetadata(ctx context.Context, invokingService string, invokedService string) (context.Context, string) {
	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(invokingService+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", CHECKOUTSERVICE)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Log sending gRPC
	event := "Sending message to " + invokedService + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	return metadataCtx, RequestID.String()
}

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
	productCatalogSvcAddr string
	cartSvcAddr           string
	currencySvcAddr       string
	shippingSvcAddr       string
	emailSvcAddr          string
	paymentSvcAddr        string
}

func main() {
	if os.Getenv("DISABLE_TRACING") == "" {
		log.Info("Tracing enabled.")
		go initTracing()
	} else {
		log.Info("Tracing disabled.")
	}

	if os.Getenv("DISABLE_PROFILER") == "" {
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

	log.Infof("service config: %+v", svc)

	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		log.Fatal(err)
	}

	var srv *grpc.Server
	if os.Getenv("DISABLE_STATS") == "" {
		log.Info("Stats enabled.")
		srv = grpc.NewServer(grpc.StatsHandler(&ocgrpc.ServerHandler{}))
	} else {
		log.Info("Stats disabled.")
		srv = grpc.NewServer()
	}
	pb.RegisterCheckoutServiceServer(srv, svc)
	healthpb.RegisterHealthServer(srv, svc)
	log.Infof("starting to listen on tcp: %q", lis.Addr().String())
	err = srv.Serve(lis)
	log.Fatal(err)
}

func initJaegerTracing() {
	svcAddr := os.Getenv("JAEGER_SERVICE_ADDR")
	if svcAddr == "" {
		log.Info("jaeger initialization disabled.")
		return
	}

	// Register the Jaeger exporter to be able to retrieve
	// the collected spans.
	exporter, err := jaeger.NewExporter(jaeger.Options{
		Endpoint: fmt.Sprintf("http://%s", svcAddr),
		Process: jaeger.Process{
			ServiceName: "checkoutservice",
		},
	})
	if err != nil {
		log.Fatal(err)
	}
	trace.RegisterExporter(exporter)
	log.Info("jaeger initialization completed.")
}

func initStats(exporter *stackdriver.Exporter) {
	view.SetReportingPeriod(60 * time.Second)
	view.RegisterExporter(exporter)
	if err := view.Register(ocgrpc.DefaultServerViews...); err != nil {
		log.Warn("Error registering default server views")
	} else {
		log.Info("Registered default server views")
	}
}

func initStackdriverTracing() {
	// TODO(ahmetb) this method is duplicated in other microservices using Go
	// since they are not sharing packages.
	for i := 1; i <= 3; i++ {
		exporter, err := stackdriver.NewExporter(stackdriver.Options{})
		if err != nil {
			log.Infof("failed to initialize stackdriver exporter: %+v", err)
		} else {
			trace.RegisterExporter(exporter)
			log.Info("registered Stackdriver tracing")

			// Register the views to collect server stats.
			initStats(exporter)
			return
		}
		d := time.Second * 10 * time.Duration(i)
		log.Infof("sleeping %v to retry initializing Stackdriver exporter", d)
		time.Sleep(d)
	}
	log.Warn("could not initialize Stackdriver exporter after retrying, giving up")
}

func initTracing() {
	initJaegerTracing()
	initStackdriverTracing()
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

func (cs *checkoutService) Check(ctx context.Context, req *healthpb.HealthCheckRequest) (*healthpb.HealthCheckResponse, error) {
	return &healthpb.HealthCheckResponse{Status: healthpb.HealthCheckResponse_SERVING}, nil
}

func (cs *checkoutService) Watch(req *healthpb.HealthCheckRequest, ws healthpb.Health_WatchServer) error {
	return status.Errorf(codes.Unimplemented, "health check via Watch not implemented")
}

func (cs *checkoutService) PlaceOrder(ctx context.Context, req *pb.PlaceOrderRequest) (*pb.PlaceOrderResponse, error) {
	RequestID, ServiceName := readMetadata(ctx)

	log.Infof("[PlaceOrder] user_id=%q user_currency=%q", req.UserId, req.UserCurrency)

	orderID, err := uuid.NewUUID()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to generate order uuid")
	}

	prep, err := cs.prepareOrderItemsAndShippingQuoteFromCart(ctx, req.UserId, req.UserCurrency, req.Address)
	if err != nil {
		return nil, status.Errorf(codes.Internal, err.Error())
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
	resp := &pb.PlaceOrderResponse{Order: orderResult}

	emitLog("Answered request from "+ServiceName+" (request_id: "+RequestID+")", "INFO")

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
	conn, err := grpc.DialContext(ctx, cs.shippingSvcAddr,
		grpc.WithInsecure(),
		grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog("could not connect shipping service: "+err.Error(), "ERROR")
		return nil, fmt.Errorf("could not connect shipping service: %+v", err)
	}
	defer conn.Close()

	// Prepare gRPC metadata and timeout
	metadataCtx, RequestID := setMetadata(ctx, CHECKOUTSERVICE, SHIPPINGSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	shippingQuote, err := pb.NewShippingServiceClient(conn).
		GetQuote(newCtx, &pb.GetQuoteRequest{
			Address: address,
			Items:   items})

	// Check gRPC reply
	checkResponse(status.Code(err), SHIPPINGSERVICE, RequestID, err)

	return shippingQuote.GetCostUsd(), nil
}

func (cs *checkoutService) getUserCart(ctx context.Context, userID string) ([]*pb.CartItem, error) {
	conn, err := grpc.DialContext(ctx, cs.cartSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog("could not connect cart service: "+err.Error(), "ERROR")
		return nil, fmt.Errorf("could not connect cart service: %+v", err)
	}
	defer conn.Close()

	// Prepare gRPC metadata and timeout
	metadataCtx, RequestID := setMetadata(ctx, CHECKOUTSERVICE, CARTSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	cart, err := pb.NewCartServiceClient(conn).GetCart(newCtx, &pb.GetCartRequest{UserId: userID})

	// Check gRPC reply
	checkResponse(status.Code(err), CARTSERVICE, RequestID, err)

	return cart.GetItems(), nil
}

func (cs *checkoutService) emptyUserCart(ctx context.Context, userID string) error {
	conn, err := grpc.DialContext(ctx, cs.cartSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog(CHECKOUTSERVICE+": could not connect cartservice: "+err.Error(), "ERROR")
		return fmt.Errorf("could not connect cart service: %+v", err)
	}
	defer conn.Close()

	// Prepare gRPC metadata and timeout
	metadataCtx, RequestID := setMetadata(ctx, CHECKOUTSERVICE, CARTSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	_, err = pb.NewCartServiceClient(conn).EmptyCart(newCtx, &pb.EmptyCartRequest{UserId: userID})

	// Check gRPC reply
	checkResponse(status.Code(err), CARTSERVICE, RequestID, err)

	return nil
}

func (cs *checkoutService) prepOrderItems(ctx context.Context, items []*pb.CartItem, userCurrency string) ([]*pb.OrderItem, error) {
	out := make([]*pb.OrderItem, len(items))

	conn, err := grpc.DialContext(ctx, cs.productCatalogSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog(CHECKOUTSERVICE+": could not connect "+PRODUCTCATALOGSERVICE+": "+err.Error(), "ERROR")
		return nil, fmt.Errorf("could not connect product catalog service: %+v", err)
	}
	defer conn.Close()
	cl := pb.NewProductCatalogServiceClient(conn)

	for i, item := range items {
		// Prepare gRPC metadata and timeout
		metadataCtx, RequestID := setMetadata(ctx, CHECKOUTSERVICE, PRODUCTCATALOGSERVICE)
		newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
		defer cancel()

		product, err := cl.GetProduct(newCtx, &pb.GetProductRequest{Id: item.GetProductId()})

		// Check gRPC reply
		checkResponse(status.Code(err), PRODUCTCATALOGSERVICE, RequestID, err)

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
	conn, err := grpc.DialContext(ctx, cs.currencySvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		return nil, fmt.Errorf("could not connect currency service: %+v", err)
	}
	defer conn.Close()

	// Prepare gRPC metadata and timeout
	metadataCtx, RequestID := setMetadata(ctx, CHECKOUTSERVICE, CURRENCYSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	result, err := pb.NewCurrencyServiceClient(conn).Convert(newCtx, &pb.CurrencyConversionRequest{
		From:   from,
		ToCode: toCurrency})

	// Check gRPC reply
	checkResponse(status.Code(err), CURRENCYSERVICE, RequestID, err)

	return result, err
}

func (cs *checkoutService) chargeCard(ctx context.Context, amount *pb.Money, paymentInfo *pb.CreditCardInfo) (string, error) {
	conn, err := grpc.DialContext(ctx, cs.paymentSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		return "", fmt.Errorf("failed to connect payment service: %+v", err)
	}
	defer conn.Close()

	// Prepare gRPC metadata and timeout
	metadataCtx, RequestID := setMetadata(ctx, CHECKOUTSERVICE, PAYMENTSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	paymentResp, err := pb.NewPaymentServiceClient(conn).Charge(newCtx, &pb.ChargeRequest{
		Amount:     amount,
		CreditCard: paymentInfo})

	// Check gRPC reply
	checkResponse(status.Code(err), PAYMENTSERVICE, RequestID, err)

	// Replaced nil with err (TESTING)
	return paymentResp.GetTransactionId(), err
}

func (cs *checkoutService) sendOrderConfirmation(ctx context.Context, email string, order *pb.OrderResult) error {
	conn, err := grpc.DialContext(ctx, cs.emailSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		return fmt.Errorf("failed to connect email service: %+v", err)
	}
	defer conn.Close()

	// Prepare gRPC metadata and timeout
	metadataCtx, RequestID := setMetadata(ctx, CHECKOUTSERVICE, EMAILSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	_, err = pb.NewEmailServiceClient(conn).SendOrderConfirmation(newCtx, &pb.SendOrderConfirmationRequest{
		Email: email,
		Order: order})

	// Check gRPC reply
	checkResponse(status.Code(err), EMAILSERVICE, RequestID, err)

	return err
}

func (cs *checkoutService) shipOrder(ctx context.Context, address *pb.Address, items []*pb.CartItem) (string, error) {
	conn, err := grpc.DialContext(ctx, cs.shippingSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		return "", fmt.Errorf("failed to connect email service: %+v", err)
	}
	defer conn.Close()

	// Prepare gRPC metadata and timeout
	metadataCtx, RequestID := setMetadata(ctx, CHECKOUTSERVICE, SHIPPINGSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	resp, err := pb.NewShippingServiceClient(conn).ShipOrder(newCtx, &pb.ShipOrderRequest{Address: address, Items: items})

	// Check gRPC reply
	checkResponse(status.Code(err), SHIPPINGSERVICE, RequestID, err)

	return resp.GetTrackingId(), nil
}

// TODO: Dial and create client once, reuse.
