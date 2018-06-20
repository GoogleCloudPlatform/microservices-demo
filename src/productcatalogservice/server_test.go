package main

import (
	"context"
	"testing"

	pb "./genproto"
	"github.com/golang/protobuf/proto"
	"github.com/google/go-cmp/cmp"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func TestServer(t *testing.T) {
	ctx := context.Background()
	addr := run(0)
	conn, err := grpc.Dial(addr, grpc.WithInsecure())
	if err != nil {
		t.Fatal(err)
	}
	defer conn.Close()
	client := pb.NewProductCatalogServiceClient(conn)
	res, err := client.ListProducts(ctx, &pb.Empty{})
	if err != nil {
		t.Fatal(err)
	}
	if diff := cmp.Diff(res.Products, catalog, cmp.Comparer(proto.Equal)); diff != "" {
		t.Error(diff)
	}

	got, err := client.GetProduct(ctx, &pb.GetProductRequest{Id: "2"})
	if err != nil {
		t.Fatal(err)
	}
	if want := catalog[1]; !proto.Equal(got, want) {
		t.Errorf("got %v, want %v", got, want)
	}
	_, err = client.GetProduct(ctx, &pb.GetProductRequest{Id: "N/A"})
	if got, want := status.Code(err), codes.NotFound; got != want {
		t.Errorf("got %s, want %s", got, want)
	}

	sres, err := client.SearchProducts(ctx, &pb.SearchProductsRequest{Query: "nice"})
	if err != nil {
		t.Fatal(err)
	}
	if diff := cmp.Diff(sres.Results, catalog, cmp.Comparer(proto.Equal)); diff != "" {
		t.Error(diff)
	}
}
