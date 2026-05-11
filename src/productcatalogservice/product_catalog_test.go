// Copyright 2023 Google LLC
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
	// Used by the 002-product-search regression: name does NOT contain "alpha"
	// but description does. Search MUST NOT return this product for query
	// "alpha" — locks in name-only matching (spec FR-004).
	mockProductCatalog.catalog.Products = append(mockProductCatalog.catalog.Products, &pb.Product{
		Id:          "abc005",
		Name:        "Watch",
		Description: "alpha numeric serial number engraved on the back",
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
	if got, want := len(products.Products), 5; got != want {
		t.Errorf("got %d, want %d", got, want)
	}
}

// TestSearchProducts exercises the 002-product-search contract semantics
// (see specs/002-product-search/contracts/search-products.proto.md):
//   - case-insensitive substring match against Product.Name only
//   - leading/trailing whitespace is trimmed
//   - empty / whitespace-only queries return no results (and never hit the catalog)
//   - description matches are NOT returned
func TestSearchProducts(t *testing.T) {
	cases := []struct {
		name      string
		query     string
		wantNames []string
	}{
		{
			name:      "exact lower-case match returns both Alpha products",
			query:     "alpha",
			wantNames: []string{"Product Alpha One", "Product Alpha Two"},
		},
		{
			name:      "upper-case query matches case-insensitively",
			query:     "ALPHA",
			wantNames: []string{"Product Alpha One", "Product Alpha Two"},
		},
		{
			name:      "mixed-case query matches case-insensitively",
			query:     "Alpha",
			wantNames: []string{"Product Alpha One", "Product Alpha Two"},
		},
		{
			name:      "leading and trailing whitespace is trimmed",
			query:     "  alpha  ",
			wantNames: []string{"Product Alpha One", "Product Alpha Two"},
		},
		{
			name:      "substring inside a name still matches",
			query:     "alp",
			wantNames: []string{"Product Alpha One", "Product Alpha Two"},
		},
		{
			name:      "exact match on a non-Alpha product",
			query:     "delta",
			wantNames: []string{"Product Delta"},
		},
		{
			name:      "single-character substring match",
			query:     "g",
			wantNames: []string{"Product Gamma"},
		},
		{
			name:      "no matches returns an empty result set",
			query:     "zzz",
			wantNames: nil,
		},
		{
			name:      "empty query returns an empty result set (does NOT return ListProducts)",
			query:     "",
			wantNames: nil,
		},
		{
			name:      "whitespace-only query returns an empty result set",
			query:     "   ",
			wantNames: nil,
		},
		{
			name:      "description-only term does NOT match (name-only semantics)",
			query:     "numeric",
			wantNames: nil,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			resp, err := mockProductCatalog.SearchProducts(context.Background(),
				&pb.SearchProductsRequest{Query: tc.query},
			)
			if err != nil {
				t.Fatalf("SearchProducts returned error: %v", err)
			}
			gotNames := make([]string, 0, len(resp.GetResults()))
			for _, p := range resp.GetResults() {
				gotNames = append(gotNames, p.GetName())
			}
			if !equalStringSlices(gotNames, tc.wantNames) {
				t.Errorf("query %q: got results %v, want %v", tc.query, gotNames, tc.wantNames)
			}
		})
	}
}

// equalStringSlices treats nil and []string{} as equivalent so a test case
// can express "no results" as `nil` without depending on the implementation
// returning a nil vs. zero-length slice.
func equalStringSlices(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}
