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
	localHost      = "127.0.0.1"
)

func main() {
	clientAddr := "thrift-demo.cart-service-port50000.checkout-system.skyramp.test"
	opt := NewDefaultOption()
	opt.HttpUrl = thriftHttpPath

	c, trans, err := NewThriftClient(clientAddr, opt)
	if err != nil {
		fmt.Printf("Failed to connect to server: %v", err)
		os.Exit(1)
	}
	err = trans.Open()
	if err != nil {
		fmt.Printf("Failed to connect to server: %v", err)
		os.Exit(1)
	}
	//
	// NOTE: Add Product to Cart
	//
	fmt.Println("connected to Cart Service")
	client := api.NewCartServiceClient(c)
	user_id := "abcde"
	product_id := "OLJCESPC7Z"
	fmt.Printf("Adding product %s to Cart\n", product_id)
	err = client.AddItem(context.Background(), user_id, &api.CartItem{ProductID: product_id, Quantity: 5})
	if err != nil {
		fmt.Printf("Failed to add item to cart: %v", err)
		os.Exit(1)
	}

	fmt.Printf("\nGet Cart\n")
	cart, err := client.GetCart(context.Background(), user_id)
	if err != nil {
		fmt.Printf("Failed to get cart: %v", err)
		os.Exit(1)
	}
	jsonProd, err := json.MarshalIndent(cart, "", "\t")
	if err != nil {
		fmt.Printf("Failed to Marshal the response from Cart Service: %v", err)
		os.Exit(1)
	}
	fmt.Println(string(jsonProd))
}
