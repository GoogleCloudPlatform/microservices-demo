package main

import (
	"context"
	"fmt"
	"os"

	api "sample-thrift/demo"
)

const (
	thriftHttpPath = "/ShippingService"
)

func main() {
	clientAddr := "thrift-demo.shipping-service-port50000.checkout-system.skyramp.test"
	opt := NewDefaultOption()
	opt.HttpUrl = thriftHttpPath

	c, trans, err := NewThriftClient(clientAddr, opt)
	if err != nil {
		fmt.Printf("Failed to connect to shipping service : %v", err)
		os.Exit(1)
	}
	err = trans.Open()
	if err != nil {
		fmt.Printf("Failed to connect to shipping service: %v", err)
		os.Exit(1)
	}
	fmt.Println("connected to the shipping service")
	client := api.NewShippingServiceClient(c)
	fmt.Println("About to call GetQuote")
	address := &api.Address{
		StreetAddress: "1600 Amp street",
		City:          "Mountain View",
		State:         "CA",
		Country:       "USA",
		ZipCode:       94043,
	}
	items := []*api.CartItem{
		{ProductID: "OLJCESPC7Z", Quantity: 1},
		{ProductID: "66VCHSJNUP", Quantity: 3},
		{ProductID: "1YMWWN1N4O", Quantity: 2},
	}

	cost, err := client.GetQuote(context.Background(), address, items)
	if err != nil {
		fmt.Printf("Failed to call ShippingService.GetQuote: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("\nSuccessfully called GetQuote: returned shipping cost [%v]]\n", cost)

	fmt.Println("About to call ShipOrder()")

	trackingId, err := client.ShipOrder(context.Background(), address, items)
	if err != nil {
		fmt.Printf("Failed to call ShippingService.ShipOrder: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("\nSuccessfully called ShippingService.ShipOrder(): returned tracking id [%s]]\n", trackingId)
}
