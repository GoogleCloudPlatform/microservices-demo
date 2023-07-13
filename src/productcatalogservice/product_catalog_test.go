// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"context"
	"os"
	"testing"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/productcatalogservice/genproto"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var (
	pc *productCatalog
)

func TestMain(m *testing.M) {
	pc = &productCatalog{
		catalog: pb.ListProductsResponse{
			Products: []*pb.Product{},
		},
	}

	pc.catalog.Products = append(pc.catalog.Products, &pb.Product{
		Id:   "abc001",
		Name: "Product Alpha One",
	})
	pc.catalog.Products = append(pc.catalog.Products, &pb.Product{
		Id:   "abc002",
		Name: "Product Delta",
	})
	pc.catalog.Products = append(pc.catalog.Products, &pb.Product{
		Id:   "abc003",
		Name: "Product Alpha Two",
	})
	pc.catalog.Products = append(pc.catalog.Products, &pb.Product{
		Id:   "abc004",
		Name: "Product Gamma",
	})

	os.Exit(m.Run())
}

func TestGetProductExists(t *testing.T) {
	product, err := pc.GetProduct(context.Background(),
		&pb.GetProductRequest{Id: "abc003"},
	)
	if err != nil {
		t.Fatal(err)
	}
	if got, want := product.Name, "Product Alpha Two"; got != want {
		t.Errorf("got %s, want %s", got, want)
	}
}

func TestGetProductNotFound(t *testing.T) {
	_, err := pc.GetProduct(context.Background(),
		&pb.GetProductRequest{Id: "abc005"},
	)
	if got, want := status.Code(err), codes.NotFound; got != want {
		t.Errorf("got %s, want %s", got, want)
	}
}

func TestListProducts(t *testing.T) {
	products, err := pc.ListProducts(context.Background(), &pb.Empty{})
	if err != nil {
		t.Fatal(err)
	}
	if got, want := len(products.Products), 4; got != want {
		t.Errorf("got %d, want %d", got, want)
	}
}

func TestSearchProducts(t *testing.T) {
	products, err := pc.SearchProducts(context.Background(),
		&pb.SearchProductsRequest{Query: "alpha"},
	)
	if err != nil {
		t.Fatal(err)
	}
	if got, want := len(products.Results), 2; got != want {
		t.Errorf("got %d, want %d", got, want)
	}
}
