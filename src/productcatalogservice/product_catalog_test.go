// Copyright 2023 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      https://www.apache.org/licenses/LICENSE-2.0
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
	"sync"
	"testing"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/productcatalogservice/genproto"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var (
	mockProductCatalog *productCatalog
)

func TestMain(m *testing.M) {
	mockProductCatalog = &productCatalog{
		catalog: pb.ListProductsResponse{
			Products: []*pb.Product{},
		},
	}

	mockProductCatalog.catalog.Products = append(mockProductCatalog.catalog.Products, &pb.Product{
		Id:   "abc001",
		Name: "Product Alpha One",
	})
	mockProductCatalog.catalog.Products = append(mockProductCatalog.catalog.Products, &pb.Product{
		Id:   "abc002",
		Name: "Product Delta",
	})
	mockProductCatalog.catalog.Products = append(mockProductCatalog.catalog.Products, &pb.Product{
		Id:   "abc003",
		Name: "Product Alpha Two",
	})
	mockProductCatalog.catalog.Products = append(mockProductCatalog.catalog.Products, &pb.Product{
		Id:   "abc004",
		Name: "Product Gamma",
	})

	os.Exit(m.Run())
}

func TestGetProductExists(t *testing.T) {
	product, err := mockProductCatalog.GetProduct(context.Background(),
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
	_, err := mockProductCatalog.GetProduct(context.Background(),
		&pb.GetProductRequest{Id: "abc005"},
	)
	if got, want := status.Code(err), codes.NotFound; got != want {
		t.Errorf("got %s, want %s", got, want)
	}
}

func TestListProducts(t *testing.T) {
	products, err := mockProductCatalog.ListProducts(context.Background(),
		&pb.Empty{},
	)
	if err != nil {
		t.Fatal(err)
	}
	if got, want := len(products.Products), 4; got != want {
		t.Errorf("got %d, want %d", got, want)
	}
}

func TestSearchProducts(t *testing.T) {
	products, err := mockProductCatalog.SearchProducts(context.Background(),
		&pb.SearchProductsRequest{Query: "alpha"},
	)
	if err != nil {
		t.Fatal(err)
	}
	if got, want := len(products.Results), 2; got != want {
		t.Errorf("got %d, want %d", got, want)
	}
}

// TestGetProductConcurrentSafe verifies that GetProduct does not panic or
// return errors when called concurrently with catalog reloads. Before the fix,
// parseCatalog() was called multiple times per loop iteration, and concurrent
// reloads could swap the slice mid-iteration causing index panics or NOT_FOUND.
func TestGetProductConcurrentSafe(t *testing.T) {
	pc := &productCatalog{
		catalog: pb.ListProductsResponse{
			Products: []*pb.Product{},
		},
	}

	// Enable catalog reloading so parseCatalog() calls loadCatalog() each time.
	// Use a product ID that exists in products.json (loaded by loadCatalog).
	reloadCatalog = true
	productID := "OLJCESPC7Z" // Sunglasses — exists in products.json

	var wg sync.WaitGroup
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 100; j++ {
				_, err := pc.GetProduct(context.Background(), &pb.GetProductRequest{Id: productID})
				if err != nil {
					t.Errorf("GetProduct failed under concurrent reload: %v", err)
				}
			}
		}()
	}
	wg.Wait()

	reloadCatalog = false
}

// TestGetProductConsistentSnapshot verifies that GetProduct returns a product
// that is actually in the catalog, even when reloads happen.
func TestGetProductConsistentSnapshot(t *testing.T) {
	pc := &productCatalog{
		catalog: pb.ListProductsResponse{
			Products: []*pb.Product{},
		},
	}

	// Even with reload enabled, every lookup should find the product.
	reloadCatalog = true
	productID := "OLJCESPC7Z" // Sunglasses — exists in products.json
	for i := 0; i < 200; i++ {
		p, err := pc.GetProduct(context.Background(), &pb.GetProductRequest{Id: productID})
		if err != nil {
			t.Fatalf("iteration %d: unexpected error: %v", i, err)
		}
		if p.Id != productID {
			t.Fatalf("iteration %d: got product %s, want %s", i, p.Id, productID)
		}
	}
	reloadCatalog = false
}
