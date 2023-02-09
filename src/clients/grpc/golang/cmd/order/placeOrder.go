package main

import (
	"context"
	"fmt"

	pb "gcp/demo"

	"google.golang.org/grpc"
)

func main() {
	conn, err := grpc.Dial("checkoutservice:5050", grpc.WithInsecure())
	if err != nil {
		fmt.Printf("Could not connect: %v\n", err)
	}

	defer conn.Close()
	c := pb.NewCheckoutServiceClient(conn)

	r, err := c.PlaceOrder(context.Background(), &pb.PlaceOrderRequest{
		UserId:       "abcde",
		UserCurrency: "USD",
		Address: &pb.Address{
			StreetAddress: "1600 Amp street",
			City:          "Mountain View",
			State:         "CA",
			Country:       "USA",
			ZipCode:       94043,
		},
		Email: "someone@example.com",
		CreditCard: &pb.CreditCardInfo{
			CreditCardNumber:          "4432-8015-6152-0454",
			CreditCardCvv:             672,
			CreditCardExpirationYear:  2024,
			CreditCardExpirationMonth: 1,
		},
	})
	if err != nil {
		fmt.Printf("Something went wrong: %v\n", err)
		return
	}

	fmt.Println("Order result: ", r.Order)
}
