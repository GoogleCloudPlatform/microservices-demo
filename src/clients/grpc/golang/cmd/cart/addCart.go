package main

import (
	"context"
	"fmt"

	pb "gcp/demo"

	"google.golang.org/grpc"
)

func main() {
	conn, err := grpc.Dial("cartservice:7070", grpc.WithInsecure())
	if err != nil {
		fmt.Printf("Could not connect: %v\n", err)
	}

	defer conn.Close()
	c := pb.NewCartServiceClient(conn)

	_, err = c.AddItem(context.Background(), &pb.AddItemRequest{
		UserId: "abcde",
		Item: &pb.CartItem{
			ProductId: "OLJCESPC7Z",
			Quantity:  1,
		},
	})
	if err != nil {
		fmt.Printf("Something went wrong: %v\n", err)
		return
	}

	fmt.Println("Successfully added the item to the cart.")
}
