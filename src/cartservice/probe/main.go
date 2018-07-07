package main

import (
	"context"
	"log"
	"os"
	"time"

	pb "./genproto"

	"google.golang.org/grpc"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		log.Fatal("probe is executed without PORT env var")
	}
	log.Printf("probe executing on port %q", port)

	conn, err := grpc.DialContext(context.TODO(),
		"localhost:"+port,
		grpc.WithInsecure(),
		grpc.WithBlock(),
		grpc.WithTimeout(time.Second*1))
	if err != nil {
		log.Fatalf("probe failed: failed to connect: %+v", err)
	}
	defer conn.Close()

	if _, err := pb.NewCartServiceClient(conn).GetCart(context.TODO(),
		&pb.GetCartRequest{UserId: "exec-probe-nonexistinguser"}); err != nil {
		log.Fatalf("probe failed: failed to query: %+v", err)
	}
	log.Println("probe successful")
}
