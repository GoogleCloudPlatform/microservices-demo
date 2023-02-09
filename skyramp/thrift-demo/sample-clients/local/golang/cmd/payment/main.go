package main

import (
	"context"
	"fmt"
	"os"

	api "sample-thrift/demo"
)

const (
	thriftHttpPath = "/PaymentService"
)

func main() {
	clientAddr := "thrift-demo.payment-service-port50000.checkout-system.skyramp.test"
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
	fmt.Println("Successfully Connected to Payment Service")
	client := api.NewPaymentServiceClient(c)

	selected_ids := []string{"OLJCESPC7Z"}
	fmt.Printf("Trying to get recommendations for product with ids[%v] \n", selected_ids)
	p, err := client.Charge(context.Background(), &api.Money{}, &api.CreditCardInfo{})
	if err != nil {
		fmt.Printf("Failed to connect to server: %v", err)
		os.Exit(1)
	}
	fmt.Printf("Result: [%s]\n", p)
}
