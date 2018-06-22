package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"

	"github.com/google/uuid"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "./genproto"
)

const (
	listenPort  = "5050"
	usdCurrency = "USD"
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

	shippingQuoteUSD, err := cs.quoteShipping(ctx, req.Address, nil) // TODO(ahmetb): query CartService for items
	if err != nil {
		return nil, status.Errorf(codes.Internal, "shipping quote failure: %+v", err)
	}
	resp.ShippingCost = &pb.Money{
		Amount:       shippingQuoteUSD,
		CurrencyCode: "USD",
	}
	// TODO(ahmetb) convert to req.UserCurrency
	// TODO(ahmetb) calculate resp.OrderItem with req.UserCurrency
	return resp, nil
}

func (cs *checkoutService) PlaceOrder(ctx context.Context, req *pb.PlaceOrderRequest) (*pb.PlaceOrderResponse, error) {
	log.Printf("[PlaceOrder] user_id=%q user_currency=%q", req.UserId, req.UserCurrency)

	orderID, err := uuid.NewUUID()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to generate order uuid")
	}

	cartItems, err := cs.getUserCart(ctx, req.UserId)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "cart failure: %+v", err)
	}

	orderItems, err := cs.prepOrderItems(ctx, cartItems, req.UserCurrency)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to prepare order: %+v", err)
	}

	shippingUsd, err := cs.quoteShipping(ctx, req.Address, cartItems) // TODO(ahmetb): query CartService for items
	if err != nil {
		return nil, status.Errorf(codes.Internal, "shipping quote failure: %+v", err)
	}
	shippingPrice, err := cs.convertCurrency(ctx, &pb.Money{
		Amount:       shippingUsd,
		CurrencyCode: usdCurrency}, req.UserCurrency)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to convert shipping cost to currency: %+v", err)
	}

	var totalPrice pb.Money
	totalPrice = sumMoney(totalPrice, *shippingPrice)
	for _, it := range orderItems {
		totalPrice = sumMoney(totalPrice, *it.Cost)
	}

	txID, err := cs.chargeCard(ctx, &totalPrice, req.CreditCard)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to charge card: %+v", err)
	}
	log.Printf("payment went through (transaction_id: %s)", txID)

	shippingTrackingID, err := cs.shipOrder(ctx, req.Address, cartItems)
	if err != nil {
		return nil, status.Errorf(codes.Unavailable, "shipping error: %+v", err)
	}

	orderResult := &pb.OrderResult{
		OrderId:            orderID.String(),
		ShippingTrackingId: shippingTrackingID,
		ShippingCost:       shippingPrice,
		ShippingAddress:    req.Address,
		Items:              orderItems,
	}

	if err := cs.sendOrderConfirmation(ctx, req.Email, orderResult); err != nil {
		log.Printf("failed to send order confirmation to %q: %+v", req.Email, err)
	} else {
		log.Printf("order confirmation email sent to %q", req.Email)
	}
	resp := &pb.PlaceOrderResponse{Order: orderResult}
	return resp, nil
}

func (cs *checkoutService) quoteShipping(ctx context.Context, address *pb.Address, items []*pb.CartItem) (*pb.MoneyAmount, error) {
	conn, err := grpc.DialContext(ctx, cs.shippingSvcAddr, grpc.WithInsecure())
	if err != nil {
		return nil, fmt.Errorf("could not connect shipping service: %+v", err)
	}
	defer conn.Close()

	shippingQuote, err := pb.NewShippingServiceClient(conn).
		GetQuote(ctx, &pb.GetQuoteRequest{
			Address: address,
			Items:   items})
	if err != nil {
		return nil, fmt.Errorf("failed to get shipping quote: %+v", err)
	}
	return shippingQuote.GetCostUsd(), nil
}

func (cs *checkoutService) getUserCart(ctx context.Context, userID string) ([]*pb.CartItem, error) {
	conn, err := grpc.DialContext(ctx, cs.cartSvcAddr, grpc.WithInsecure())
	if err != nil {
		return nil, fmt.Errorf("could not connect cart service: %+v", err)
	}
	defer conn.Close()

	cart, err := pb.NewCartServiceClient(conn).GetCart(ctx, &pb.GetCartRequest{UserId: userID})
	if err != nil {
		return nil, fmt.Errorf("failed to get user cart: %+v", err)
	}
	return cart.GetItems(), nil
}

func (cs *checkoutService) prepOrderItems(ctx context.Context, items []*pb.CartItem, userCurrency string) ([]*pb.OrderItem, error) {
	out := make([]*pb.OrderItem, len(items))

	conn, err := grpc.DialContext(ctx, cs.productCatalogSvcAddr, grpc.WithInsecure())
	if err != nil {
		return nil, fmt.Errorf("could not connect product catalog service: %+v", err)
	}
	defer conn.Close()
	cl := pb.NewProductCatalogServiceClient(conn)

	for i, item := range items {
		product, err := cl.GetProduct(ctx, &pb.GetProductRequest{Id: item.GetProductId()})
		if err != nil {
			return nil, fmt.Errorf("failed to get product #%q", item.GetProductId())
		}
		usdPrice := &pb.Money{
			Amount:       product.GetPriceUsd(),
			CurrencyCode: usdCurrency}
		price, err := cs.convertCurrency(ctx, usdPrice, userCurrency)
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
	conn, err := grpc.DialContext(ctx, cs.currencySvcAddr, grpc.WithInsecure())
	if err != nil {
		return nil, fmt.Errorf("could not connect currency service: %+v", err)
	}
	defer conn.Close()
	result, err := pb.NewCurrencyServiceClient(conn).Convert(context.TODO(), &pb.CurrencyConversionRequest{
		From:   from,
		ToCode: toCurrency})
	if err != nil {
		return nil, fmt.Errorf("failed to convert currency: %+v", err)
	}
	return result, err
}

func (cs *checkoutService) chargeCard(ctx context.Context, amount *pb.Money, paymentInfo *pb.CreditCardInfo) (string, error) {
	conn, err := grpc.DialContext(ctx, cs.paymentSvcAddr, grpc.WithInsecure())
	if err != nil {
		return "", fmt.Errorf("failed to connect payment service: %+v", err)
	}
	defer conn.Close()

	paymentResp, err := pb.NewPaymentServiceClient(conn).Charge(ctx, &pb.ChargeRequest{
		Amount:     amount,
		CreditCard: paymentInfo})
	if err != nil {
		return "", fmt.Errorf("could not charge the card: %+v", err)
	}
	return paymentResp.GetTransactionId(), nil
}

func (cs *checkoutService) sendOrderConfirmation(ctx context.Context, email string, order *pb.OrderResult) error {
	conn, err := grpc.DialContext(ctx, cs.emailSvcAddr, grpc.WithInsecure())
	if err != nil {
		return fmt.Errorf("failed to connect email service: %+v", err)
	}
	defer conn.Close()
	_, err = pb.NewEmailServiceClient(conn).SendOrderConfirmation(ctx, &pb.SendOrderConfirmationRequest{
		Email: email,
		Order: order})
	return err
}

func (cs *checkoutService) shipOrder(ctx context.Context, address *pb.Address, items []*pb.CartItem) (string, error) {
	conn, err := grpc.DialContext(ctx, cs.shippingSvcAddr, grpc.WithInsecure())
	if err != nil {
		return "", fmt.Errorf("failed to connect email service: %+v", err)
	}
	defer conn.Close()
	resp, err := pb.NewShippingServiceClient(conn).ShipOrder(ctx, &pb.ShipOrderRequest{
		Address: address,
		Items:   items})
	if err != nil {
		return "", fmt.Errorf("shipment failed: %+v", err)
	}
	return resp.GetTrackingId(), nil
}
