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
	"strings"
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

	// Existing fixtures — preserved unchanged so the existing
	// TestSearchProducts ("alpha" → 2 results) keeps passing.
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

	// Fixtures added for spec 008-product-search.
	//
	// abc005 — Name does NOT contain "lens", but Description does.
	// Used by TestSearchProducts_DescriptionOnlyMatches (AS 6 — the regression
	// guard for the "search-misses-descriptions" seed bug).
	mockProductCatalog.catalog.Products = append(mockProductCatalog.catalog.Products, &pb.Product{
		Id:          "abc005",
		Name:        "Sunglasses",
		Description: "Add a modern touch to your outfit with these stylish lenses for sun protection",
	})
	// abc006 — Name contains "lens". Combined with abc005, a query for "lens"
	// must return both products (one matched via name, one via description),
	// each exactly once. AS 6a.
	mockProductCatalog.catalog.Products = append(mockProductCatalog.catalog.Products, &pb.Product{
		Id:          "abc006",
		Name:        "Lens Kit",
		Description: "Professional photography accessory",
	})
	// abc007 — Categories contain "cameras" but Name and Description do not.
	// Used by TestSearchProducts_CategoryOnlyDoesNotMatch to guard against
	// scope creep into other product fields. AS 6b.
	mockProductCatalog.catalog.Products = append(mockProductCatalog.catalog.Products, &pb.Product{
		Id:          "abc007",
		Name:        "Tripod Mount",
		Description: "Sturdy mount for stability during long exposures",
		Categories:  []string{"cameras"},
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
	// Previously used "abc005" which is now a real fixture. "abc999" is clearly
	// outside the fixture range and stays definitely-not-found as fixtures grow.
	_, err := mockProductCatalog.GetProduct(context.Background(),
		&pb.GetProductRequest{Id: "abc999"},
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
	// 4 existing fixtures + 3 added for spec 008-product-search = 7.
	if got, want := len(products.Products), 7; got != want {
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

// ----------------------------------------------------------------------------
// Tests added by spec 008-product-search.
//
// They share the package-level mockProductCatalog initialised in TestMain
// and exercise the acceptance scenarios from specs/008-product-search/spec.md
// and the test matrix in specs/008-product-search/research.md (R-4).
//
// Convention: tests assert on result IDs rather than just counts where the
// distinction matters, so failures point at the wrong product.
// ----------------------------------------------------------------------------

// searchIDs runs SearchProducts with the given query and returns the result IDs.
func searchIDs(t *testing.T, q string) []string {
	t.Helper()
	resp, err := mockProductCatalog.SearchProducts(context.Background(),
		&pb.SearchProductsRequest{Query: q},
	)
	if err != nil {
		t.Fatalf("SearchProducts(%q) returned error: %v", q, err)
	}
	ids := make([]string, 0, len(resp.Results))
	for _, p := range resp.Results {
		ids = append(ids, p.Id)
	}
	return ids
}

// containsID returns true if ids contains id.
func containsID(ids []string, id string) bool {
	for _, v := range ids {
		if v == id {
			return true
		}
	}
	return false
}

// AS 1 — exact name returns the product.
func TestSearchProducts_ExactName(t *testing.T) {
	ids := searchIDs(t, "Product Alpha One")
	if !containsID(ids, "abc001") {
		t.Errorf("query %q should include abc001; got %v", "Product Alpha One", ids)
	}
}

// AS 2 — substring at the start of the name.
func TestSearchProducts_Substring_Start(t *testing.T) {
	// "Prod" begins every existing-fixture name (Product Alpha One/Two, Delta, Gamma).
	// None of the new-fixture names start with "Prod" and none of the new descriptions
	// contain "Prod" (case-insensitively); "Professional" does NOT contain "prod".
	ids := searchIDs(t, "Prod")
	for _, expected := range []string{"abc001", "abc002", "abc003", "abc004"} {
		if !containsID(ids, expected) {
			t.Errorf("query %q should include %s; got %v", "Prod", expected, ids)
		}
	}
}

// AS 2 — substring in the middle of the name.
func TestSearchProducts_Substring_Middle(t *testing.T) {
	ids := searchIDs(t, "lph")
	for _, expected := range []string{"abc001", "abc003"} {
		if !containsID(ids, expected) {
			t.Errorf("query %q should include %s; got %v", "lph", expected, ids)
		}
	}
}

// AS 2 — substring at the end of the name.
func TestSearchProducts_Substring_End(t *testing.T) {
	ids := searchIDs(t, "Two")
	if !containsID(ids, "abc003") {
		t.Errorf("query %q should include abc003; got %v", "Two", ids)
	}
}

// AS 3 — uppercase query matches mixed-case name.
func TestSearchProducts_CaseInsensitive_Upper(t *testing.T) {
	ids := searchIDs(t, "ALPHA")
	for _, expected := range []string{"abc001", "abc003"} {
		if !containsID(ids, expected) {
			t.Errorf("query %q should include %s; got %v", "ALPHA", expected, ids)
		}
	}
}

// AS 4 — mixed-case query matches.
func TestSearchProducts_CaseInsensitive_Mixed(t *testing.T) {
	ids := searchIDs(t, "AlPhA")
	for _, expected := range []string{"abc001", "abc003"} {
		if !containsID(ids, expected) {
			t.Errorf("query %q should include %s; got %v", "AlPhA", expected, ids)
		}
	}
}

// AS 5 — multiple matches.
func TestSearchProducts_MultipleMatches(t *testing.T) {
	ids := searchIDs(t, "Alpha")
	if got, want := len(ids), 2; got != want {
		t.Errorf("query %q expected %d matches; got %d (%v)", "Alpha", want, got, ids)
	}
}

// AS 6 (amended) — description-only match.
// abc005 has "lens" in its description but NOT in its name. It MUST appear.
// This is the regression guard for the "search-misses-descriptions" seed bug.
func TestSearchProducts_DescriptionOnlyMatches(t *testing.T) {
	// Sanity: abc005's name does not contain "lens". If this assertion ever
	// fails, the fixture was changed and the test no longer proves what it claims.
	if strings.Contains(strings.ToLower("Sunglasses"), "lens") {
		t.Fatal("test fixture is broken: abc005 name unexpectedly contains \"lens\"")
	}

	ids := searchIDs(t, "lens")
	if !containsID(ids, "abc005") {
		t.Errorf("query %q should include abc005 (matched via description); got %v", "lens", ids)
	}
}

// AS 6a — query matches abc005 via description AND abc006 via name; both appear, each once.
func TestSearchProducts_NameAndDescriptionBothMatch(t *testing.T) {
	ids := searchIDs(t, "lens")
	for _, expected := range []string{"abc005", "abc006"} {
		count := 0
		for _, id := range ids {
			if id == expected {
				count++
			}
		}
		if count != 1 {
			t.Errorf("query %q should include %s exactly once; appeared %d times in %v", "lens", expected, count, ids)
		}
	}
}

// AS 6b — category-only does NOT match.
// abc007's category is "cameras" but its name and description do not contain "cameras".
// The query "cameras" must NOT return abc007.
func TestSearchProducts_CategoryOnlyDoesNotMatch(t *testing.T) {
	ids := searchIDs(t, "cameras")
	if containsID(ids, "abc007") {
		t.Errorf("query %q should NOT include abc007 (matches only on category, which is out of scope); got %v", "cameras", ids)
	}
}

// AS 7 — no match returns empty.
func TestSearchProducts_NoMatch(t *testing.T) {
	ids := searchIDs(t, "xyznonsense")
	if len(ids) != 0 {
		t.Errorf("query %q expected 0 matches; got %v", "xyznonsense", ids)
	}
}

// Edge case — special characters are treated as literal substring text, not regex.
// "$" does not appear in any fixture name or description.
func TestSearchProducts_SpecialChars(t *testing.T) {
	ids := searchIDs(t, "$")
	if len(ids) != 0 {
		t.Errorf("query %q should be treated literally and match nothing; got %v", "$", ids)
	}
}

// Edge case — a query longer than any name or description returns zero matches.
func TestSearchProducts_LongQuery(t *testing.T) {
	long := strings.Repeat("longquerythatcannotappear", 20) // 500 chars
	ids := searchIDs(t, long)
	if len(ids) != 0 {
		t.Errorf("over-long query expected 0 matches; got %v", ids)
	}
}

// FR-007 — results are in catalog iteration order, not re-sorted.
// abc001 ("Product Alpha One") was appended before abc003 ("Product Alpha Two")
// in TestMain; the result order must reflect this.
func TestSearchProducts_NaturalOrder(t *testing.T) {
	ids := searchIDs(t, "Alpha")
	if len(ids) < 2 {
		t.Fatalf("query %q expected >=2 matches; got %v", "Alpha", ids)
	}
	if ids[0] != "abc001" || ids[1] != "abc003" {
		t.Errorf("expected catalog order [abc001, abc003]; got %v", ids)
	}
}
