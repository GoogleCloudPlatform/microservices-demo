// Copyright 2024 Google LLC
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

package validator

import (
	"strings"
	"testing"
)

func TestPlaceOrderPassesValidation(t *testing.T) {
	tests := []struct {
		name          string
		email         string
		streetAddress string
		zipCode       int64
		city          string
		state         string
		country       string
		ccNumber      string
		ccMonth       int64
		ccYear        int64
		ccCVV         int64
	}{
		{"valid", "test@example.com", "12345 example street", 10004, "New York", "New York", "United States", "5272940000751666", 4, 2024, 584},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			payload := PlaceOrderPayload{
				Email:         tt.email,
				StreetAddress: tt.streetAddress,
				ZipCode:       tt.zipCode,
				City:          tt.city,
				State:         tt.state,
				Country:       tt.country,
				CcNumber:      tt.ccNumber,
				CcMonth:       tt.ccMonth,
				CcYear:        tt.ccYear,
				CcCVV:         tt.ccCVV,
			}
			if err := payload.Validate(); err != nil {
				t.Errorf("want validation on %v, got %v", payload, err)
			}
		})
	}
}

func TestPlaceOrderFailsValidation(t *testing.T) {
	tests := []struct {
		name          string
		email         string
		streetAddress string
		zipCode       int64
		city          string
		state         string
		country       string
		ccNumber      string
		ccMonth       int64
		ccYear        int64
		ccCVV         int64
	}{
		{"invalid email", "test@example", "12345 example street", 10004, "New York", "New York", "United States", "5272940000751666", 4, 2024, 584},
		{"invalid address (too long)", "test@example.com", strings.Repeat("12345 example street", 513), 10004, "New York", "New York", "United States", "5272940000751666", 4, 2024, 584},
		{"invalid zip code", "test@example.com", "12345 example street", 0, "New York", "New York", "United States", "5272940000751666", 4, 2024, 584},
		{"invalid city", "test@example.com", "12345 example street", 10004, "", "New York", "United States", "5272940000751666", 4, 2024, 584},
		{"invalid state", "test@example.com", "12345 example street", 10004, "New York", "", "United States", "5272940000751666", 4, 2024, 584},
		{"invalid country", "test@example.com", "12345 example street", 10004, "New York", "New York", "", "5272940000751666", 4, 2024, 584},
		{"invalid ccNumber", "test@example.com", "12345 example street", 10004, "New York", "New York", "United States", "5272940000", 4, 2024, 584},
		{"invalid ccMonth (month < 1)", "test@example.com", "12345 example street", 10004, "New York", "New York", "United States", "5272940000751666", 0, 2024, 584},
		{"invalid ccMonth (month > 12)", "test@example.com", "12345 example street", 10004, "New York", "New York", "United States", "5272940000751666", 13, 2024, 584},
		{"invalid ccYear (not provided)", "test@example.com", "12345 example street", 10004, "New York", "New York", "United States", "5272940000751666", 12, 0, 584},
		{"invalid ccCVV (not provided)", "test@example.com", "12345 example street", 10004, "New York", "New York", "United States", "5272940000751666", 12, 2024, 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			payload := PlaceOrderPayload{
				Email:         tt.email,
				StreetAddress: tt.streetAddress,
				ZipCode:       tt.zipCode,
				City:          tt.city,
				State:         tt.state,
				Country:       tt.country,
				CcNumber:      tt.ccNumber,
				CcMonth:       tt.ccMonth,
				CcYear:        tt.ccYear,
				CcCVV:         tt.ccCVV,
			}
			if err := payload.Validate(); err == nil {
				t.Errorf("want validation on %v, got %v", payload, err)
			}
		})
	}
}

func TestAddToCartPassesValidation(t *testing.T) {
	tests := []struct {
		name      string
		quantity  uint64
		productID string
	}{
		{"valid min quantity and product id", 1, "OLJCESPC7Z"},
		{"valid max quantity and product id", 10, "OLJCESPC7Z"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			payload := AddToCartPayload{Quantity: tt.quantity, ProductID: tt.productID}
			if err := payload.Validate(); err != nil {
				t.Errorf("want validation on %v, got %v", payload, err)
			}
		})
	}
}

func TestAddToCartFailsValidation(t *testing.T) {
	tests := []struct {
		name      string
		quantity  uint64
		productID string
	}{
		{"invalid min quantity", 0, "OLJCESPC7Z"},
		{"invalid max quantity", 11, "OLJCESPC7Z"},
		{"invalid product id", 1, ""},
		{"invalid quantity and product id", 0, ""},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			payload := AddToCartPayload{Quantity: tt.quantity, ProductID: tt.productID}
			if err := payload.Validate(); err == nil {
				t.Errorf("want validation on %v, got %v", payload, err)
			}
		})
	}
}

func TestSetCurrencyPassesValidation(t *testing.T) {
	tests := []struct {
		name     string
		currency string
	}{
		{"valid currency (EUR)", "EUR"},
		{"valid currency (USD)", "USD"},
		{"valid currency (JPY)", "JPY"},
		{"valid currency (GBP)", "GBP"},
		{"valid currency (TRY)", "TRY"},
		{"valid currency (CAD)", "CAD"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			payload := SetCurrencyPayload{Currency: tt.currency}
			if err := payload.Validate(); err != nil {
				t.Errorf("want validation on %v, got %v", payload, err)
			}
		})
	}
}

func TestSetCurrencyFailsValidation(t *testing.T) {
	tests := []struct {
		name     string
		currency string
	}{
		{"invalid currency", "ABC"},
		{"invalid currency (symbol)", "$"},
		{"invalid (no currency)", ""},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			payload := SetCurrencyPayload{Currency: tt.currency}
			if err := payload.Validate(); err == nil {
				t.Errorf("want validation on %v, got %v", payload, err)
			}
		})
	}
}
