package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"database/sql"
	"fmt"
	"net"
	"os"
	"time"

	"github.com/go-sql-driver/mysql"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/health"
	"google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/status"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice/genproto"
)

var (
	log *logrus.Logger
	db  *sql.DB
)

func init() {
	log = logrus.New()
	log.Level = logrus.InfoLevel
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
	emailSvcAddr          string
	paymentSvcAddr        string
	shippingSvcAddr       string
	pb.UnimplementedCheckoutServiceServer
}

func main() {
	initDB()
	defer db.Close()

	port := os.Getenv("PORT")
	if port == "" {
		port = "5050"
	}

	svc := new(checkoutService)
	mustMapEnv(&svc.cartSvcAddr, "CART_SERVICE_ADDR")
	mustMapEnv(&svc.currencySvcAddr, "CURRENCY_SERVICE_ADDR")
	mustMapEnv(&svc.productCatalogSvcAddr, "PRODUCT_CATALOG_SERVICE_ADDR")
	mustMapEnv(&svc.shippingSvcAddr, "SHIPPING_SERVICE_ADDR")
	mustMapEnv(&svc.paymentSvcAddr, "PAYMENT_SERVICE_ADDR")
	mustMapEnv(&svc.emailSvcAddr, "EMAIL_SERVICE_ADDR")

	log.Infof("service config: %+v", svc)

	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		log.Fatal(err)
	}

	srv := grpc.NewServer()

	// ==> THIS IS THE FIX <==
	// Register the gRPC health check service.
	healthSrv := health.NewServer()
	grpc_health_v1.RegisterHealthServer(srv, healthSrv)
	healthSrv.SetServingStatus("checkoutservice", grpc_health_v1.HealthCheckResponse_SERVING)
	// =======================

	pb.RegisterCheckoutServiceServer(srv, svc)
	log.Infof("starting gRPC server on port %s", port)
	if err := srv.Serve(lis); err != nil {
		log.Fatal(err)
	}
}

func mustMapEnv(target *string, envKey string) {
	v := os.Getenv(envKey)
	if v == "" {
		panic(fmt.Sprintf("environment variable %q not set", envKey))
	}
	*target = v
}

func initDB() {
	dbUser := os.Getenv("MYSQL_USER")
	dbPassword := os.Getenv("MYSQL_PASSWORD")
	dbHost := os.Getenv("MYSQL_HOST")
	dbPort := os.Getenv("MYSQL_PORT")
	dbName := os.Getenv("MYSQL_DATABASE")
	sslCertPath := os.Getenv("SSL_CERT_PATH")

	// This block registers the custom TLS config using your cert
	if sslCertPath != "" {
		rootCertPool := x509.NewCertPool()
		pem, err := os.ReadFile(sslCertPath)
		if err != nil {
			log.Fatalf("failed to read CA cert: %v", err)
		}
		if ok := rootCertPool.AppendCertsFromPEM(pem); !ok {
			log.Fatal("failed to append PEM.")
		}
		mysql.RegisterTLSConfig("custom", &tls.Config{
			RootCAs: rootCertPool,
		})
	}

	// The DSN now uses "tls=custom" to use the registered cert
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?parseTime=true&tls=custom", dbUser, dbPassword, dbHost, dbPort, dbName)

	var err error
	db, err = sql.Open("mysql", dsn)
	if err != nil {
		log.Fatalf("failed to open database connection: %v", err)
	}

	db.SetConnMaxLifetime(time.Minute * 3)
	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(10)

	err = db.Ping()
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}
	log.Info("Successfully connected to MySQL database")
}

func (cs *checkoutService) PlaceOrder(ctx context.Context, req *pb.PlaceOrderRequest) (*pb.PlaceOrderResponse, error) {
	log.Infof("[PlaceOrder] user_id=%q, user_currency=%q", req.UserId, req.UserCurrency)

	orderID, err := uuid.NewRandom()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to generate order id: %v", err)
	}

	prep, err := cs.prepareOrderItemsAndShippingQuoteFromCart(ctx, req.UserId, req.UserCurrency, req.Address)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "error preparing order: %v", err)
	}

	total := &pb.Money{CurrencyCode: req.UserCurrency, Units: 0, Nanos: 0}
	total, err = sum(total, prep.shippingCostLocalized)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to sum money: %v", err)
	}
	for _, it := range prep.orderItems {
		multPrice, err := multiplySlow(it.Cost, uint32(it.Item.Quantity))
		if err != nil {
			return nil, status.Errorf(codes.Internal, "failed to multiply money: %v", err)
		}
		total, err = sum(total, multPrice)
		if err != nil {
			return nil, status.Errorf(codes.Internal, "failed to sum money: %v", err)
		}
	}

	txID, err := cs.chargeCreditCard(ctx, total, req)
	if err != nil {
		return nil, fmt.Errorf("failed to charge credit card: %w", err)
	}
	log.Infof("payment went through (transaction_id: %s)", txID)

	shippingTrackingID, err := cs.shipOrder(ctx, req.Address, prep.cartItems)
	if err != nil {
		return nil, fmt.Errorf("failed to ship order: %w", err)
	}
	log.Infof("shipping tracking id: %s", shippingTrackingID)

	if err := InsertOrder(ctx, orderID.String(), shippingTrackingID, total, req.Address, prep.orderItems); err != nil {
		log.Errorf("failed to insert order into database: %v", err)
	}

	if err := cs.emptyUserCart(ctx, req.UserId); err != nil {
		log.Warnf("failed to empty user cart: %v", err)
	}

	orderResult := &pb.OrderResult{
		OrderId:            orderID.String(),
		ShippingTrackingId: shippingTrackingID,
		ShippingCost:       prep.shippingCostLocalized,
		ShippingAddress:    req.Address,
		Items:              prep.orderItems,
	}

	if err := cs.sendOrderConfirmation(ctx, req.Email, orderResult); err != nil {
		log.Warnf("failed to send order confirmation to %q: %v", req.Email, err)
	} else {
		log.Infof("order confirmation email sent to %q", req.Email)
	}

	return &pb.PlaceOrderResponse{Order: orderResult}, nil
}

func InsertOrder(ctx context.Context, orderID, trackingID string, total *pb.Money, address *pb.Address, items []*pb.OrderItem) error {
	itemsJSON := "[]"

	_, err := db.ExecContext(ctx, `
		INSERT INTO orders (order_id, shipping_tracking_id, shipping_cost_usd_currency_code, shipping_cost_usd_units, shipping_cost_usd_nanos, shipping_address_street_address, shipping_address_city, shipping_address_state, shipping_address_country, shipping_address_zip_code, items)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		orderID, trackingID, total.CurrencyCode, total.Units, total.Nanos, address.StreetAddress, address.City, address.State, address.Country, address.ZipCode, itemsJSON)
	return err
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
		return out, fmt.Errorf("failed to get user cart: %w", err)
	}
	orderItems, err := cs.getProducts(ctx, cartItems)
	if err != nil {
		return out, fmt.Errorf("failed to get products: %w", err)
	}
	shippingUSD, err := cs.quoteShipping(ctx, address, cartItems)
	if err != nil {
		return out, fmt.Errorf("failed to quote shipping: %w", err)
	}
	shippingPrice, err := cs.convertCurrency(ctx, shippingUSD, userCurrency)
	if err != nil {
		return out, fmt.Errorf("failed to convert shipping cost to user currency: %w", err)
	}

	out.shippingCostLocalized = shippingPrice
	out.cartItems = cartItems
	out.orderItems = orderItems
	return out, nil
}

func (cs *checkoutService) quoteShipping(ctx context.Context, address *pb.Address, items []*pb.CartItem) (*pb.Money, error) {
	conn, err := grpc.Dial(cs.shippingSvcAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, fmt.Errorf("could not connect to %s: %w", cs.shippingSvcAddr, err)
	}
	defer conn.Close()

	shippingQuote, err := pb.NewShippingServiceClient(conn).
		GetQuote(ctx, &pb.GetQuoteRequest{
			Address: address,
			Items:   items,
		})
	if err != nil {
		return nil, fmt.Errorf("failed to get shipping quote: %w", err)
	}
	return shippingQuote.GetCostUsd(), nil
}

func (cs *checkoutService) getUserCart(ctx context.Context, userID string) ([]*pb.CartItem, error) {
	conn, err := grpc.Dial(cs.cartSvcAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, fmt.Errorf("could not connect to %s: %w", cs.cartSvcAddr, err)
	}
	defer conn.Close()

	cart, err := pb.NewCartServiceClient(conn).GetCart(ctx, &pb.GetCartRequest{UserId: userID})
	if err != nil {
		return nil, fmt.Errorf("failed to get user cart: %w", err)
	}
	return cart.GetItems(), nil
}

func (cs *checkoutService) emptyUserCart(ctx context.Context, userID string) error {
	conn, err := grpc.Dial(cs.cartSvcAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return fmt.Errorf("could not connect to %s: %w", cs.cartSvcAddr, err)
	}
	defer conn.Close()

	if _, err = pb.NewCartServiceClient(conn).EmptyCart(ctx, &pb.EmptyCartRequest{UserId: userID}); err != nil {
		return fmt.Errorf("failed to empty user cart: %w", err)
	}
	return nil
}

func (cs *checkoutService) getProducts(ctx context.Context, items []*pb.CartItem) ([]*pb.OrderItem, error) {
	conn, err := grpc.Dial(cs.productCatalogSvcAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, fmt.Errorf("could not connect to %s: %w", cs.productCatalogSvcAddr, err)
	}
	defer conn.Close()
	cl := pb.NewProductCatalogServiceClient(conn)

	out := make([]*pb.OrderItem, len(items))
	for i, item := range items {
		product, err := cl.GetProduct(ctx, &pb.GetProductRequest{Id: item.GetProductId()})
		if err != nil {
			return nil, fmt.Errorf("failed to get product #%q: %w", item.GetProductId(), err)
		}
		out[i] = &pb.OrderItem{
			Item: item,
			Cost: product.GetPriceUsd(),
		}
	}
	return out, nil
}

func (cs *checkoutService) convertCurrency(ctx context.Context, from *pb.Money, toCurrency string) (*pb.Money, error) {
	conn, err := grpc.Dial(cs.currencySvcAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, fmt.Errorf("could not connect to %s: %w", cs.currencySvcAddr, err)
	}
	defer conn.Close()

	result, err := pb.NewCurrencyServiceClient(conn).
		Convert(ctx, &pb.CurrencyConversionRequest{
			From:   from,
			ToCode: toCurrency,
		})
	if err != nil {
		return nil, fmt.Errorf("failed to convert currency: %w", err)
	}
	return result, nil
}

func (cs *checkoutService) chargeCreditCard(ctx context.Context, amount *pb.Money, req *pb.PlaceOrderRequest) (string, error) {
	conn, err := grpc.Dial(cs.paymentSvcAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return "", fmt.Errorf("failed to connect to %s: %w", cs.paymentSvcAddr, err)
	}
	defer conn.Close()

	paymentResp, err := pb.NewPaymentServiceClient(conn).Charge(ctx, &pb.ChargeRequest{
		Amount:     amount,
		CreditCard: req.GetCreditCard(),
	})
	if err != nil {
		return "", status.Errorf(codes.Internal, "failed to charge card: %v", err)
	}
	return paymentResp.GetTransactionId(), nil
}

func (cs *checkoutService) sendOrderConfirmation(ctx context.Context, email string, order *pb.OrderResult) error {
	conn, err := grpc.Dial(cs.emailSvcAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return fmt.Errorf("failed to connect to %s: %w", cs.emailSvcAddr, err)
	}
	defer conn.Close()

	_, err = pb.NewEmailServiceClient(conn).SendOrderConfirmation(ctx, &pb.SendOrderConfirmationRequest{
		Email: email,
		Order: order,
	})
	return err
}

func (cs *checkoutService) shipOrder(ctx context.Context, address *pb.Address, items []*pb.CartItem) (string, error) {
	conn, err := grpc.Dial(cs.shippingSvcAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return "", fmt.Errorf("failed to connect to %s: %w", cs.shippingSvcAddr, err)
	}
	defer conn.Close()
	resp, err := pb.NewShippingServiceClient(conn).ShipOrder(ctx, &pb.ShipOrderRequest{
		Address: address,
		Items:   items,
	})
	if err != nil {
		return "", status.Errorf(codes.Unavailable, "shipping service unavailable: %v", err)
	}
	return resp.GetTrackingId(), nil
}

const (
	nanosInUnit = 1000000000
)

func sum(l, r *pb.Money) (*pb.Money, error) {
	if l.GetCurrencyCode() != r.GetCurrencyCode() {
		return nil, fmt.Errorf("mismatched currency codes: %s vs %s", l.GetCurrencyCode(), r.GetCurrencyCode())
	}
	out := &pb.Money{
		CurrencyCode: l.GetCurrencyCode(),
		Units:        l.GetUnits() + r.GetUnits(),
		Nanos:        l.GetNanos() + r.GetNanos(),
	}

	if out.Nanos >= nanosInUnit {
		out.Units += int64(out.Nanos / nanosInUnit)
		out.Nanos %= nanosInUnit
	} else if out.Nanos <= -nanosInUnit {
		out.Units += int64(out.Nanos / nanosInUnit)
		out.Nanos %= -nanosInUnit
	}
	return out, nil
}

func multiplySlow(m *pb.Money, n uint32) (*pb.Money, error) {
	out := &pb.Money{CurrencyCode: m.GetCurrencyCode()}
	out.Units = m.GetUnits() * int64(n)
	out.Nanos = m.GetNanos() * int32(n)

	if out.Nanos >= nanosInUnit {
		out.Units += int64(out.Nanos / nanosInUnit)
		out.Nanos = out.Nanos % nanosInUnit
	}
	return out, nil
}
