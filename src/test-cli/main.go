package main

import (
	"context"
	"log"
	"os"

	pb "./genproto"
	"google.golang.org/grpc"
)

type test struct {
	envs []string
	f    func() error
}

var (
	svcs = map[string]test{
		"productcatalogservice": {
			envs: []string{"PRODUCT_CATALOG_SERVICE_ADDR"},
			f:    testProductCatalogService,
		},
		"shippingservice": {
			envs: []string{"SHIPPING_SERVICE_ADDR"},
			f:    testShippingService,
		},
		"recommendationservice": {
			envs: []string{"RECOMMENDATION_SERVICE_ADDR"},
			f:    testRecommendationService,
		},
		"paymentservice": {
			envs: []string{"PAYMENT_SERVICE_ADDR"},
			f:    testPaymentService,
		},
		"emailservice": {
			envs: []string{"EMAIL_SERVICE_ADDR"},
			f:    testEmailService,
		},
		"currencyservice": {
			envs: []string{"CURRENCY_SERVICE_ADDR"},
			f:    testCurrencyService,
		},
	}
)

func main() {
	if len(os.Args) != 2 {
		panic("incorrect usage")
	}
	t, ok := svcs[os.Args[1]]
	if !ok {
		log.Fatalf("test probe for %q not found", os.Args[1])
	}
	for _, e := range t.envs {
		if os.Getenv(e) == "" {
			log.Fatalf("environment variable %q not set", e)
		}
	}
	log.Printf("smoke test %q", os.Args[1])
	if err := t.f(); err != nil {
		panic(err)
	}
	log.Println("PASS")
}

func testProductCatalogService() error {
	addr := os.Getenv("PRODUCT_CATALOG_SERVICE_ADDR")
	conn, err := grpc.Dial(addr, grpc.WithInsecure())
	if err != nil {
		return err
	}
	defer conn.Close()

	log.Printf("--- rpc ListProducts() ")
	cl := pb.NewProductCatalogServiceClient(conn)
	listResp, err := cl.ListProducts(context.TODO(), &pb.Empty{})
	if err != nil {
		return err
	}
	log.Printf("--> %d products returned", len(listResp.GetProducts()))
	for _, v := range listResp.GetProducts() {
		log.Printf("--> %+v", v)
	}

	log.Println("--- rpc GetProduct()")
	getResp, err := cl.GetProduct(context.TODO(), &pb.GetProductRequest{Id: "1"})
	if err != nil {
		return err
	}
	log.Printf("retrieved product: %+v", getResp)
	log.Printf("--- rpc SearchProducts()")
	searchResp, err := cl.SearchProducts(context.TODO(), &pb.SearchProductsRequest{Query: "shirt"})
	if err != nil {
		return err
	}
	log.Printf("--> %d results found", len(searchResp.GetResults()))

	return nil
}

func testShippingService() error {
	addr := os.Getenv("SHIPPING_SERVICE_ADDR")
	conn, err := grpc.Dial(addr, grpc.WithInsecure())
	if err != nil {
		return err
	}
	defer conn.Close()

	address := &pb.Address{
		StreetAddress_1: "Muffin Man",
		StreetAddress_2: "Drury Lane",
		City:            "London",
		Country:         "United Kingdom",
	}
	items := []*pb.CartItem{
		{
			ProductId: "23",
			Quantity:  10,
		},
		{
			ProductId: "46",
			Quantity:  3,
		},
	}

	log.Println("--- rpc GetQuote()")
	cl := pb.NewShippingServiceClient(conn)
	quoteResp, err := cl.GetQuote(context.TODO(), &pb.GetQuoteRequest{
		Address: address,
		Items:   items})
	if err != nil {
		return err
	}
	log.Printf("--> quote: %+v", quoteResp)

	log.Println("--- rpc ShipOrder()")
	shipResp, err := cl.ShipOrder(context.TODO(), &pb.ShipOrderRequest{
		Address: address,
		Items:   items})
	if err != nil {
		return err
	}
	log.Printf("--> quote: %+v", shipResp)
	return nil
}

func testRecommendationService() error {
	addr := os.Getenv("RECOMMENDATION_SERVICE_ADDR")
	conn, err := grpc.Dial(addr, grpc.WithInsecure())
	if err != nil {
		return err
	}
	defer conn.Close()
	cl := pb.NewRecommendationServiceClient(conn)

	log.Println("--- rpc ShipOrder()")
	resp, err := cl.ListRecommendations(context.TODO(), &pb.ListRecommendationsRequest{
		UserId:     "foo",
		ProductIds: []string{"1", "2", "3", "4", "5"},
	})
	if err != nil {
		return err
	}
	log.Printf("--> returned %d recommendations", len(resp.GetProductIds()))
	log.Printf("--> ids: %v", resp.GetProductIds())
	return nil
}

func testPaymentService() error {
	addr := os.Getenv("RECOMMENDATION_SERVICE_ADDR")
	conn, err := grpc.Dial(addr, grpc.WithInsecure())
	if err != nil {
		return err
	}
	defer conn.Close()
	cl := pb.NewPaymentServiceClient(conn)

	log.Println("--- rpc Charge()")
	resp, err := cl.Charge(context.TODO(), &pb.ChargeRequest{
		Amount: &pb.Money{
			CurrencyCode: "USD",
			Amount: &pb.MoneyAmount{
				Decimal:    10,
				Fractional: 55},
		},
		CreditCard: &pb.CreditCardInfo{
			CreditCardNumber:          "9999-9999-9999-9999",
			CreditCardCvv:             612,
			CreditCardExpirationYear:  2022,
			CreditCardExpirationMonth: 10},
	})
	if err != nil {
		return nil
	}
	log.Printf("--> resp: %+v", resp)
	return nil
}

func testEmailService() error {
	addr := os.Getenv("EMAIL_SERVICE_ADDR")
	conn, err := grpc.Dial(addr, grpc.WithInsecure())
	if err != nil {
		return err
	}
	defer conn.Close()
	cl := pb.NewEmailServiceClient(conn)
	log.Println("--- rpc SendOrderConfirmation()")
	resp, err := cl.SendOrderConfirmation(context.TODO(), &pb.SendOrderConfirmationRequest{
		Email: "noreply@example.com",
		Order: &pb.OrderResult{
			OrderId:            "123456",
			ShippingTrackingId: "000-123-456",
			ShippingCost: &pb.Money{
				CurrencyCode: "CAD",
				Amount: &pb.MoneyAmount{
					Decimal:    10,
					Fractional: 55},
			},
			ShippingAddress: &pb.Address{
				StreetAddress_1: "Muffin Man",
				StreetAddress_2: "Drury Lane",
				City:            "London",
				Country:         "United Kingdom",
			},
			Items: []*pb.OrderItem{
				&pb.OrderItem{
					Item: &pb.CartItem{
						ProductId: "1",
						Quantity:  4},
					Cost: &pb.Money{
						CurrencyCode: "CAD",
						Amount: &pb.MoneyAmount{
							Decimal:    120,
							Fractional: 0}},
				},
				&pb.OrderItem{
					Item: &pb.CartItem{
						ProductId: "2",
						Quantity:  1},
					Cost: &pb.Money{
						CurrencyCode: "CAD",
						Amount: &pb.MoneyAmount{
							Decimal:    12,
							Fractional: 25}},
				},
			},
		},
	})
	if err != nil {
		return err
	}
	log.Printf("--> resp: %+v", resp)
	return nil
}

func testCurrencyService() error {
	addr := os.Getenv("CURRENCY_SERVICE_ADDR")
	conn, err := grpc.Dial(addr, grpc.WithInsecure())
	if err != nil {
		return err
	}
	defer conn.Close()
	cl := pb.NewCurrencyServiceClient(conn)
	log.Println("--- rpc GetSupportedCurrencies()")
	listResp, err := cl.GetSupportedCurrencies(context.TODO(), &pb.Empty{})
	if err != nil {
		return err
	}
	log.Printf("--> returned %d currency codes", len(listResp.GetCurrencyCodes()))
	log.Printf("--> %v", listResp.GetCurrencyCodes())

	log.Println("--- rpc Convert()")
	convertResp, err := cl.Convert(context.TODO(), &pb.CurrencyConversionRequest{
		From: &pb.Money{
			CurrencyCode: "CAD",
			Amount: &pb.MoneyAmount{
				Decimal:    12,
				Fractional: 25},
		},
		ToCode: "USD"})
	if err != nil {
		return err
	}
	log.Printf("--> result: %+v", convertResp)
	return nil
}
