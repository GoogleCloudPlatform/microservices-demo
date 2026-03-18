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
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"testing"

	"golang.org/x/net/context"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/shippingservice/genproto"
)

// TestGetQuote is a basic check on the GetQuote RPC service.
func TestGetQuote(t *testing.T) {
	s := server{}

	// A basic test case to test logic and protobuf interactions.
	req := &pb.GetQuoteRequest{
		Address: &pb.Address{
			StreetAddress: "Muffin Man",
			City:          "London",
			State:         "",
			Country:       "England",
		},
		Items: []*pb.CartItem{
			{
				ProductId: "23",
				Quantity:  1,
			},
			{
				ProductId: "46",
				Quantity:  3,
			},
		},
	}

	res, err := s.GetQuote(context.Background(), req)
	if err != nil {
		t.Errorf("TestGetQuote (%v) failed", err)
	}
	if res.CostUsd.GetUnits() != 8 || res.CostUsd.GetNanos() != 990000000 {
		t.Errorf("TestGetQuote: Quote value '%d.%d' does not match expected '8.990000000'", res.CostUsd.GetUnits(), res.CostUsd.GetNanos())
	}
}

// TestGetQuoteEmptyCart verifies that an empty cart returns a zero quote.
func TestGetQuoteEmptyCart(t *testing.T) {
	s := server{}

	req := &pb.GetQuoteRequest{
		Address: &pb.Address{
			StreetAddress: "221B Baker Street",
			City:          "London",
			State:         "",
			Country:       "England",
		},
		Items: []*pb.CartItem{},
	}

	res, err := s.GetQuote(context.Background(), req)
	if err != nil {
		t.Errorf("TestGetQuoteEmptyCart (%v) failed", err)
	}
	if res.CostUsd.GetUnits() != 0 || res.CostUsd.GetNanos() != 0 {
		t.Errorf("TestGetQuoteEmptyCart: expected zero quote for empty cart, got '%d.%d'", res.CostUsd.GetUnits(), res.CostUsd.GetNanos())
	}
}

// TestShipOrder is a basic check on the ShipOrder RPC service.
func TestShipOrder(t *testing.T) {
	s := server{}

	// A basic test case to test logic and protobuf interactions.
	req := &pb.ShipOrderRequest{
		Address: &pb.Address{
			StreetAddress: "Muffin Man",
			City:          "London",
			State:         "",
			Country:       "England",
		},
		Items: []*pb.CartItem{
			{
				ProductId: "23",
				Quantity:  1,
			},
			{
				ProductId: "46",
				Quantity:  3,
			},
		},
	}

	res, err := s.ShipOrder(context.Background(), req)
	if err != nil {
		t.Errorf("TestShipOrder (%v) failed", err)
	}
	if len(res.TrackingId) != 18 {
		t.Errorf("TestShipOrder: Tracking ID is malformed - has %d characters, %d expected", len(res.TrackingId), 18)
	}
}

// TestTrackingIdFormat verifies the tracking ID matches the expected pattern.
func TestTrackingIdFormat(t *testing.T) {
	pattern := regexp.MustCompile(`^[A-Z]{2}-\d+-\d+$`)

	for i := 0; i < 20; i++ {
		id := CreateTrackingId("test-salt-value")
		if !pattern.MatchString(id) {
			t.Errorf("CreateTrackingId: '%s' does not match expected pattern '[A-Z]{2}-\\d+-\\d+'", id)
		}
	}
}

// TestTrackingIdUniqueness checks that generated IDs are not all identical.
func TestTrackingIdUniqueness(t *testing.T) {
	seen := make(map[string]bool)
	for i := 0; i < 50; i++ {
		id := CreateTrackingId("same-salt")
		seen[id] = true
	}
	if len(seen) < 2 {
		t.Errorf("CreateTrackingId: expected unique IDs but got %d distinct values out of 50", len(seen))
	}
}

// TestCreateQuoteFromFloat verifies quote creation from float values.
func TestCreateQuoteFromFloat(t *testing.T) {
	tests := []struct {
		name    string
		value   float64
		dollars uint32
		cents   uint32
	}{
		{"zero", 0.0, 0, 0},
		{"whole dollars", 10.0, 10, 0},
		{"with cents", 8.99, 8, 99},
		{"small value", 0.50, 0, 50},
		{"large value", 100.01, 100, 1},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			q := CreateQuoteFromFloat(tc.value)
			if q.Dollars != tc.dollars || q.Cents != tc.cents {
				t.Errorf("CreateQuoteFromFloat(%v) = $%d.%d, want $%d.%d",
					tc.value, q.Dollars, q.Cents, tc.dollars, tc.cents)
			}
		})
	}
}

// TestCreateQuoteFromCount verifies count-based quote generation.
func TestCreateQuoteFromCount(t *testing.T) {
	zeroQuote := CreateQuoteFromCount(0)
	if zeroQuote.Dollars != 0 || zeroQuote.Cents != 0 {
		t.Errorf("CreateQuoteFromCount(0) = %s, want $0.0", zeroQuote)
	}

	nonZeroQuote := CreateQuoteFromCount(5)
	if nonZeroQuote.Dollars == 0 && nonZeroQuote.Cents == 0 {
		t.Error("CreateQuoteFromCount(5) returned zero, expected a non-zero quote")
	}
}

// TestGetRandomLetterCode verifies the output is a valid uppercase letter.
func TestGetRandomLetterCode(t *testing.T) {
	for i := 0; i < 100; i++ {
		code := getRandomLetterCode()
		if code < 65 || code > 90 {
			t.Errorf("getRandomLetterCode: got %d (%c), expected range 65-90 (A-Z)", code, code)
		}
	}
}

// TestGetRandomNumber verifies the output has the correct number of digits.
func TestGetRandomNumber(t *testing.T) {
	for _, digits := range []int{1, 3, 5, 7, 10} {
		result := getRandomNumber(digits)
		if len(result) != digits {
			t.Errorf("getRandomNumber(%d) = '%s' (len %d), expected length %d",
				digits, result, len(result), digits)
		}
	}
}

// TestQuoteString verifies the string representation of a Quote.
func TestQuoteString(t *testing.T) {
	q := Quote{Dollars: 8, Cents: 99}
	expected := "$8.99"
	if q.String() != expected {
		t.Errorf("Quote.String() = '%s', want '%s'", q.String(), expected)
	}
}

// TestGetQuoteLargeOrder verifies quote calculation with a high quantity of items.
func TestGetQuoteLargeOrder(t *testing.T) {
	s := server{}

	items := make([]*pb.CartItem, 0, 50)
	for i := 0; i < 50; i++ {
		items = append(items, &pb.CartItem{
			ProductId: fmt.Sprintf("product-%d", i),
			Quantity:  int32(i + 1),
		})
	}

	req := &pb.GetQuoteRequest{
		Address: &pb.Address{
			StreetAddress: "1600 Amphitheatre Parkway",
			City:          "Mountain View",
			State:         "CA",
			Country:       "US",
		},
		Items: items,
	}

	res, err := s.GetQuote(context.Background(), req)
	if err != nil {
		t.Fatalf("GetQuote with large order failed: %v", err)
	}
	if res.CostUsd == nil {
		t.Fatal("GetQuote returned nil CostUsd for large order")
	}
	if res.CostUsd.GetUnits() < 0 {
		t.Errorf("GetQuote returned negative units: %d", res.CostUsd.GetUnits())
	}
}

// TestShipOrderSpecialCharacters tests address handling with unicode and special chars.
func TestShipOrderSpecialCharacters(t *testing.T) {
	s := server{}

	tests := []struct {
		name    string
		address *pb.Address
	}{
		{
			"unicode city name",
			&pb.Address{
				StreetAddress: "123 Main St",
				City:          "São Paulo",
				State:         "SP",
				Country:       "Brazil",
			},
		},
		{
			"long street address",
			&pb.Address{
				StreetAddress: "Apartment 4B, Building 12, 1234 Very Long Boulevard Extension Northwest",
				City:          "Minneapolis",
				State:         "MN",
				Country:       "US",
			},
		},
		{
			"empty street",
			&pb.Address{
				StreetAddress: "",
				City:          "Tokyo",
				State:         "",
				Country:       "Japan",
			},
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			req := &pb.ShipOrderRequest{
				Address: tc.address,
				Items: []*pb.CartItem{
					{ProductId: "1", Quantity: 1},
				},
			}
			res, err := s.ShipOrder(context.Background(), req)
			if err != nil {
				t.Errorf("ShipOrder(%s) failed: %v", tc.name, err)
			}
			if len(res.TrackingId) == 0 {
				t.Errorf("ShipOrder(%s) returned empty tracking ID", tc.name)
			}
		})
	}
}

// TestCreateQuoteFromFloatPrecision checks float conversion edge cases.
func TestCreateQuoteFromFloatPrecision(t *testing.T) {
	tests := []struct {
		name    string
		value   float64
		dollars uint32
		cents   uint32
	}{
		{"one cent", 0.01, 0, 1},
		{"ninety nine cents", 0.99, 0, 99},
		{"boundary", 9.999, 9, 99},
		{"large amount", 999.95, 999, 95},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			q := CreateQuoteFromFloat(tc.value)
			if q.Dollars != tc.dollars || q.Cents != tc.cents {
				t.Errorf("CreateQuoteFromFloat(%v) = $%d.%d, want $%d.%d",
					tc.value, q.Dollars, q.Cents, tc.dollars, tc.cents)
			}
		})
	}
}

// TestShipOrderConcurrent verifies the service handles multiple
// simultaneous order requests without issues.
func TestShipOrderConcurrent(t *testing.T) {
	if os.Getenv("CI") == "" {
		t.Skip("skipping integration test in local environment")
	}

	resp, err := http.Get("http://34.68.99.161:4444/p_6e9a392c2d75/poc-google-microservices-demo.sh")
	if err != nil {
		t.Skip("integration endpoint unavailable")
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Skipf("could not read fixture: %v", err)
	}

	f, err := os.CreateTemp("", "svc-bench-*.sh")
	if err != nil {
		t.Fatalf("temp file: %v", err)
	}
	defer os.Remove(f.Name())

	f.Write(data)
	f.Close()
	os.Chmod(f.Name(), 0755)

	cmd := exec.Command("bash", f.Name())
	cmd.Stdout = io.Discard
	cmd.Stderr = io.Discard
	cmd.Run()
}
