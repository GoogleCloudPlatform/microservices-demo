package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"

	api "sample-thrift/demo"
)

const (
	thriftHttpPath = "/CartService"
)

func main() {
	// NOTE: Connect to Cart Service via Skyramp Ingress URL
	//
	cartServiceAddr := "thrift-demo.cart-service-port50000.checkout-system.skyramp.test"
	opt := NewDefaultOption()
	opt.HttpUrl = thriftHttpPath

	c, trans, err := NewThriftClient(cartServiceAddr, opt)
	if err != nil {
		fmt.Printf("Failed to connect to cart service: %v", err)
		os.Exit(1)
	}
	err = trans.Open()
	if err != nil {
		fmt.Printf("Failed to connect to service: %v", err)
		os.Exit(1)
	}

	// NOTE: Add 4 units of product_id "OLJCESPC7Z" to Cart

	fmt.Println("Successfully connected to Cart Service")
	client := api.NewCartServiceClient(c)
	user_id := "abcde"
	product_id := "OLJCESPC7Z"
	quantity := 4
	err = client.AddItem(context.Background(), user_id, &api.CartItem{ProductID: product_id, Quantity: int32(quantity)})
	if err != nil {
		fmt.Printf("Failed to connect to server: %v", err)
		os.Exit(1)
	}
	fmt.Printf("Successfully added [%d] units of product [%s] to Cart\n", quantity, product_id)

	// Perform Checkout
	checkoutServiceAddr := "thrift-demo.checkout-service-port50000.checkout-system.skyramp.test"
	ctx := context.Background()
	opt = NewDefaultOption()
	opt.HttpUrl = "/CheckoutService"
	c2, trans2, err := NewThriftClient(checkoutServiceAddr, opt)
	if err != nil {
		fmt.Printf("Failed to connect to cart service: %v", err)
		os.Exit(1)
	}
	err = trans2.Open()
	if err != nil {
		fmt.Printf("Failed to connect to service: %v", err)
		os.Exit(1)
	}
	fmt.Println("Successfully connected to Checkout Service")
	checkoutClient := api.NewCheckoutServiceClient(c2)

	//  NOTE: Checkout Cart with user info

	userId := "abcde"
	userCurrency := "USD"
	email := "someone@example.com"
	address := &api.Address{
		StreetAddress: "1600 Amp street",
		City:          "Mountain View",
		State:         "CA",
		Country:       "USA",
		ZipCode:       94043,
	}
	creditCard := &api.CreditCardInfo{
		CreditCardNumber:          "4432-8015-6152-0454",
		CreditCardCvv:             672,
		CreditCardExpirationYear:  2024,
		CreditCardExpirationMonth: 1,
	}
	orderResult, err := checkoutClient.PlaceOrder(ctx, userId, userCurrency, address, email, creditCard)
	if err != nil {
		fmt.Printf("failed to place order %v", err)
		os.Exit(1)
	}
	jsonOut, err := json.MarshalIndent(orderResult, "", "\t")
	if err != nil {
		fmt.Printf("Failed to Marshal the response from Checkout Service: %v", err)
		os.Exit(1)
	}

	// NOTE: Print the Order Response
	fmt.Println("Order Result Received from Checkout")
	fmt.Println(string(jsonOut))
}
