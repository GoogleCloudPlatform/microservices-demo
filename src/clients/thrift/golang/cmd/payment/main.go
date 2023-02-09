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
	clientAddr := "paymentservice:50000"
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

	amount := &api.Money{CurrencyCode: "USD", Units: 100, Nanos: 99999}
	creditCard := &api.CreditCardInfo{
		CreditCardNumber:          "4432-8015-6152-0454",
		CreditCardCvv:             672,
		CreditCardExpirationYear:  2024,
		CreditCardExpirationMonth: 1,
	}

	p, err := client.Charge(context.Background(), amount, creditCard)
	if err != nil {
		fmt.Printf("Failed to connect to server: %v", err)
		os.Exit(1)
	}
	fmt.Printf("Result: [%s]\n", p)
}
