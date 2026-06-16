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
	"testing"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"
)

func TestPromoDiscountRate(t *testing.T) {
	tests := []struct {
		code   string
		want   float64
		wantOK bool
	}{
		{"50OFF", 0.50, true},
		{"50off", 0.50, true},
		{"  50off  ", 0.50, true},
		{"UNKNOWN", 0, false},
		{"", 0, false},
	}
	for _, tt := range tests {
		got, ok := promoDiscountRate(tt.code)
		if ok != tt.wantOK || got != tt.want {
			t.Errorf("promoDiscountRate(%q) = (%v, %v), want (%v, %v)", tt.code, got, ok, tt.want, tt.wantOK)
		}
	}
}

func TestDiscountAmount(t *testing.T) {
	// $40.00 basket -> 50% -> $20.00 discount.
	d := discountAmount(pb.Money{CurrencyCode: "USD", Units: 40, Nanos: 0}, 0.50)
	if d.GetUnits() != 20 || d.GetNanos() != 0 || d.GetCurrencyCode() != "USD" {
		t.Errorf("discountAmount(40.00, 0.50) = %d.%09d %s, want 20.000000000 USD", d.GetUnits(), d.GetNanos(), d.GetCurrencyCode())
	}

	// $40.50 basket -> 50% -> $20.25 discount.
	d2 := discountAmount(pb.Money{CurrencyCode: "USD", Units: 40, Nanos: 500000000}, 0.50)
	if d2.GetUnits() != 20 || d2.GetNanos() != 250000000 {
		t.Errorf("discountAmount(40.50, 0.50) = %d.%09d, want 20.250000000", d2.GetUnits(), d2.GetNanos())
	}
}
