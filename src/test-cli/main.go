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
	getResp, err := cl.GetProduct(context.TODO(), &pb.GetProductRequest{Id: 1})
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
