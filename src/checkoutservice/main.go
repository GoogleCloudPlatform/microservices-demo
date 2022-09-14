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
	"google.golang.org/grpc/metadata"
	"net"
	"os"
	"time"

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
	listenPort  = "5050"
	usdCurrency = "USD"
	SERVICENAME = "checkoutservice"
)

// NOTE: logLevel must be a GELF valid severity value (WARN or ERROR), INFO if not specified
func emitLog(event string, logLevel string) {
	logMessage := time.Now().Format(time.RFC3339) + " - " + logLevel + " - " + SERVICENAME + " - " + event

	switch logLevel {
	case "ERROR":
		log.Error(logMessage)
	case "WARN":
		log.Warn(logMessage)
	default:
		log.Info(logMessage)
	}
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
	md, _ := metadata.FromIncomingContext(ctx)
	reqId := md.Get("requestid")
	invService := md.Get("servicename")
	var RequestID, ServiceName string

	if len(reqId) > 0 && len(invService) > 0 {
		RequestID = reqId[0]
		ServiceName = invService[0]
		emitLog("Received request from "+ServiceName+" (request_id: "+RequestID+")", "INFO")

	} else {
		emitLog(SERVICENAME+": An error occurred while retrieving the RequestID", "ERROR")
	}

	log.Infof("[PlaceOrder] user_id=%q user_currency=%q", req.UserId, req.UserCurrency)

	orderID, err := uuid.NewUUID()
	if err != nil {
		emitLog(SERVICENAME+": failed to generate order uuid", "ERROR")
		return nil, status.Errorf(codes.Internal, "failed to generate order uuid")
	}

	prep, err := cs.prepareOrderItemsAndShippingQuoteFromCart(ctx, req.UserId, req.UserCurrency, req.Address)
	if err != nil {
		emitLog(SERVICENAME+": "+err.Error(), "ERROR")
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
		emitLog(SERVICENAME+": failed to charge card: "+err.Error(), "ERROR")
		return nil, status.Errorf(codes.Internal, "failed to charge card: %+v", err)
	}
	log.Infof("payment went through (transaction_id: %s)", txID)

	shippingTrackingID, err := cs.shipOrder(ctx, req.Address, prep.cartItems)
	if err != nil {
		emitLog(SERVICENAME+": shipping error "+err.Error(), "ERROR")
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
		emitLog(SERVICENAME+": failed to send order confirmation to "+req.Email+": "+err.Error(), "WARN")
		log.Warnf("failed to send order confirmation to %q: %+v", req.Email, err)
	} else {
		log.Infof("order confirmation email sent to %q", req.Email)
	}
	resp := &pb.PlaceOrderResponse{Order: orderResult}

	event := "Answered to request from " + ServiceName + " (request_id: " + RequestID + ")"
	emitLog(event, "INFO")

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
		emitLog(SERVICENAME+": cart failure: "+err.Error(), "ERROR")
		return out, fmt.Errorf("cart failure: %+v", err)
	}
	orderItems, err := cs.prepOrderItems(ctx, cartItems, userCurrency)
	if err != nil {
		emitLog(SERVICENAME+": failed to prepare order: "+err.Error(), "ERROR")
		return out, fmt.Errorf("failed to prepare order: %+v", err)
	}
	shippingUSD, err := cs.quoteShipping(ctx, address, cartItems)
	if err != nil {
		emitLog(SERVICENAME+": shipping quote failure: "+err.Error(), "ERROR")
		return out, fmt.Errorf("shipping quote failure: %+v", err)
	}
	shippingPrice, err := cs.convertCurrency(ctx, shippingUSD, userCurrency)
	if err != nil {
		emitLog(SERVICENAME+": failed to convert shipping cost to currency: "+err.Error(), "ERROR")
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

	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(SERVICENAME+": An error occurred while generating the RequestID", "ERROR")
	}

	header := metadata.Pairs("requestid", RequestID.String(), "servicename", SERVICENAME)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	newCtx, cancel := context.WithTimeout(metadataCtx, 2*time.Second)
	defer cancel()

	event := "Sending message to SHIPPINGSERVICE (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	shippingQuote, err := pb.NewShippingServiceClient(conn).
		GetQuote(newCtx, &pb.GetQuoteRequest{
			Address: address,
			Items:   items})

	receivedCode := status.Code(err)

	if receivedCode == codes.DeadlineExceeded {
		event = "Failing to contact SHIPPINGSERVICE (request_id: " + RequestID.String() + "). Root cause: (" + newCtx.Err().Error() + ")"
		emitLog(event, "ERROR")

	} else if err != nil {
		event = "Error response received from SHIPPINGSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "ERROR")
		return nil, fmt.Errorf("failed to get shipping quote: %+v", err)

	} else {
		event = "Receiving answer from SHIPPINGSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "INFO")
	}

	return shippingQuote.GetCostUsd(), nil
}

func (cs *checkoutService) getUserCart(ctx context.Context, userID string) ([]*pb.CartItem, error) {
	conn, err := grpc.DialContext(ctx, cs.cartSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog("could not connect cart service: "+err.Error(), "ERROR")
		return nil, fmt.Errorf("could not connect cart service: %+v", err)
	}
	defer conn.Close()

	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(SERVICENAME+": An error occurred while generating the RequestID", "ERROR")
	}

	header := metadata.Pairs("requestid", RequestID.String(), "servicename", SERVICENAME)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	newCtx, cancel := context.WithTimeout(metadataCtx, 2*time.Second)
	defer cancel()

	event := "Sending message to CARTSERVICE (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	cart, err := pb.NewCartServiceClient(conn).GetCart(newCtx, &pb.GetCartRequest{UserId: userID})

	receivedCode := status.Code(err)

	if receivedCode == codes.DeadlineExceeded {
		event = "Failing to contact SHIPPINGSERVICE (request_id: " + RequestID.String() + "). Root cause: (" + newCtx.Err().Error() + ")"
		emitLog(event, "ERROR")

	} else if err != nil {
		event = "Error response received from SHIPPINGSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "ERROR")
		return nil, fmt.Errorf("failed to get user cart during checkout: %+v", err)

	} else {
		event = "Receiving answer from SHIPPINGSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "INFO")
	}

	return cart.GetItems(), nil
}

func (cs *checkoutService) emptyUserCart(ctx context.Context, userID string) error {
	conn, err := grpc.DialContext(ctx, cs.cartSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog(SERVICENAME+"could not connect cart service: "+err.Error(), "ERROR")
		return fmt.Errorf("could not connect cart service: %+v", err)
	}
	defer conn.Close()

	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(SERVICENAME+": An error occurred while generating the RequestID", "ERROR")
	}

	event := "Sending message to CARTSERVICE (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	header := metadata.Pairs("requestid", RequestID.String(), "servicename", SERVICENAME)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	newCtx, cancel := context.WithTimeout(metadataCtx, 2*time.Second)
	defer cancel()

	_, err = pb.NewCartServiceClient(conn).EmptyCart(newCtx, &pb.EmptyCartRequest{UserId: userID})
	receivedCode := status.Code(err)

	if receivedCode == codes.DeadlineExceeded {
		event = "Failing to contact CARTSERVICE (request_id: " + RequestID.String() + "). Root cause: (" + newCtx.Err().Error() + ")"
		emitLog(event, "ERROR")

	} else if err != nil {
		event = "Error response received from CARTSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "ERROR")
		return fmt.Errorf("failed to empty user cart during checkout: %+v", err)

	} else {
		event = "Receiving answer from CARTSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "INFO")
	}

	return nil
}

func (cs *checkoutService) prepOrderItems(ctx context.Context, items []*pb.CartItem, userCurrency string) ([]*pb.OrderItem, error) {
	out := make([]*pb.OrderItem, len(items))

	conn, err := grpc.DialContext(ctx, cs.productCatalogSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog(SERVICENAME+"could not connect product catalog service: "+err.Error(), "ERROR")
		return nil, fmt.Errorf("could not connect product catalog service: %+v", err)
	}
	defer conn.Close()
	cl := pb.NewProductCatalogServiceClient(conn)

	for i, item := range items {
		RequestID, err := uuid.NewRandom()
		if err != nil {
			emitLog(SERVICENAME+": An error occurred while generating the RequestID", "ERROR")
		}

		header := metadata.Pairs("requestid", RequestID.String(), "servicename", SERVICENAME)
		metadataCtx := metadata.NewOutgoingContext(ctx, header)

		newCtx, cancel := context.WithTimeout(metadataCtx, 2*time.Second)
		defer cancel()

		event := "Sending message to PRODUCTCATALOG (request_id: " + RequestID.String() + ")"
		emitLog(event, "INFO")

		product, err := cl.GetProduct(newCtx, &pb.GetProductRequest{Id: item.GetProductId()})

		receivedCode := status.Code(err)

		if receivedCode == codes.DeadlineExceeded {
			event = "Failing to contact PRODUCTCATALOG (request_id: " + RequestID.String() + "). Root cause: (" + newCtx.Err().Error() + ")"
			emitLog(event, "ERROR")

		} else if err != nil {
			event = "Error response received from PRODUCTCATALOG (request_id: " + RequestID.String() + ")"
			emitLog(event, "ERROR")
			return nil, fmt.Errorf("failed to get product #%q", item.GetProductId())

		} else {
			event = "Receiving answer from PRODUCTCATALOG (request_id: " + RequestID.String() + ")"
			emitLog(event, "INFO")
		}

		price, err := cs.convertCurrency(ctx, product.GetPriceUsd(), userCurrency)
		if err != nil {
			emitLog(SERVICENAME+": failed to convert price of "+item.GetProductId()+" to "+userCurrency, "ERROR")
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
		emitLog(SERVICENAME+"could not connect currency service: "+err.Error(), "ERROR")
		return nil, fmt.Errorf("could not connect currency service: %+v", err)
	}
	defer conn.Close()

	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(SERVICENAME+": An error occurred while generating the RequestID", "ERROR")
	}

	header := metadata.Pairs("requestid", RequestID.String(), "servicename", SERVICENAME)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	newCtx, cancel := context.WithTimeout(metadataCtx, 2*time.Second)
	defer cancel()

	event := "Sending message to CURRENCYSERVICE (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	result, err := pb.NewCurrencyServiceClient(conn).Convert(newCtx, &pb.CurrencyConversionRequest{
		From:   from,
		ToCode: toCurrency})

	receivedCode := status.Code(err)

	if receivedCode == codes.DeadlineExceeded {
		event = "Failing to contact CURRENCYSERVICE (request_id: " + RequestID.String() + "). Root cause: (" + newCtx.Err().Error() + ")"
		emitLog(event, "ERROR")
	} else if err != nil {
		event = "Error response received from CURRENCYSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "ERROR")
		return nil, fmt.Errorf("failed to convert currency: %+v", err)
	} else {
		event = "Receiving answer from CURRENCYSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "INFO")
	}

	return result, err
}

func (cs *checkoutService) chargeCard(ctx context.Context, amount *pb.Money, paymentInfo *pb.CreditCardInfo) (string, error) {
	conn, err := grpc.DialContext(ctx, cs.paymentSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog(SERVICENAME+"failed to connect payment service: "+err.Error(), "ERROR")
		return "", fmt.Errorf("failed to connect payment service: %+v", err)
	}
	defer conn.Close()

	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(SERVICENAME+": An error occurred while generating the RequestID", "ERROR")
	}

	header := metadata.Pairs("requestid", RequestID.String(), "servicename", SERVICENAME)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	newCtx, cancel := context.WithTimeout(metadataCtx, 2*time.Second)
	defer cancel()

	event := "Sending message to PAYMENTSERVICE (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	paymentResp, err := pb.NewPaymentServiceClient(conn).Charge(newCtx, &pb.ChargeRequest{
		Amount:     amount,
		CreditCard: paymentInfo})

	receivedCode := status.Code(err)

	if receivedCode == codes.DeadlineExceeded {
		event = "Failing to contact PAYMENTSERVICE (request_id: " + RequestID.String() + "). Root cause: (" + newCtx.Err().Error() + ")"
		emitLog(event, "ERROR")

	} else if err != nil {
		event = "Error response received from PAYMENTSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "ERROR")
		return "", fmt.Errorf("could not charge the card: %+v", err)

	} else {
		event = "Receiving answer from PAYMENTSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "INFO")
	}

	return paymentResp.GetTransactionId(), nil
}

func (cs *checkoutService) sendOrderConfirmation(ctx context.Context, email string, order *pb.OrderResult) error {
	conn, err := grpc.DialContext(ctx, cs.emailSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog(SERVICENAME+"failed to connect email service: "+err.Error(), "ERROR")
		return fmt.Errorf("failed to connect email service: %+v", err)
	}
	defer conn.Close()

	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(SERVICENAME+": An error occurred while generating the RequestID", "ERROR")
	}

	header := metadata.Pairs("requestid", RequestID.String(), "servicename", SERVICENAME)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	newCtx, cancel := context.WithTimeout(metadataCtx, 2*time.Second)
	defer cancel()

	event := "Sending message to EMAILSERVICE (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	_, err = pb.NewEmailServiceClient(conn).SendOrderConfirmation(newCtx, &pb.SendOrderConfirmationRequest{
		Email: email,
		Order: order})

	receivedCode := status.Code(err)

	if receivedCode == codes.DeadlineExceeded {
		event = "Failing to contact EMAILSERVICE (request_id: " + RequestID.String() + "). Root cause: (" + newCtx.Err().Error() + ")"
		emitLog(event, "ERROR")

	} else if err != nil {
		event = "Error response received from EMAILSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "ERROR")

	} else {
		event = "Receiving answer from EMAILSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "INFO")
	}

	return err
}

func (cs *checkoutService) shipOrder(ctx context.Context, address *pb.Address, items []*pb.CartItem) (string, error) {
	conn, err := grpc.DialContext(ctx, cs.shippingSvcAddr, grpc.WithInsecure(), grpc.WithStatsHandler(&ocgrpc.ClientHandler{}))
	if err != nil {
		emitLog(SERVICENAME+"failed to connect email service: "+err.Error(), "ERROR")
		return "", fmt.Errorf("failed to connect email service: %+v", err)
	}
	defer conn.Close()

	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(SERVICENAME+": An error occurred while generating the RequestID", "ERROR")
	}

	header := metadata.Pairs("requestid", RequestID.String(), "servicename", SERVICENAME)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	newCtx, cancel := context.WithTimeout(metadataCtx, 2*time.Second)
	defer cancel()

	event := "Sending message to SHIPPINGSERVICE (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	resp, err := pb.NewShippingServiceClient(conn).ShipOrder(newCtx, &pb.ShipOrderRequest{Address: address, Items: items})

	receivedCode := status.Code(err)

	if receivedCode == codes.DeadlineExceeded {
		event = "Failing to contact SHIPPINGSERVICE (request_id: " + RequestID.String() + "). Root cause: (" + newCtx.Err().Error() + ")"
		emitLog(event, "ERROR")

	} else if err != nil {
		event = "Error response received from SHIPPINGSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "ERROR")
		return "", fmt.Errorf("shipment failed: %+v", err)

	} else {
		event = "Receiving answer from SHIPPINGSERVICE (request_id: " + RequestID.String() + ")"
		emitLog(event, "INFO")
	}

	return resp.GetTrackingId(), nil
}

// TODO: Dial and create client once, reuse.
