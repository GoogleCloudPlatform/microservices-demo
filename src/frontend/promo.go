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
	"strings"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"
)

// promoCodes is the hardcoded, in-memory set of valid promo codes mapped to
// their discount rate (a fraction of the basket items total). Additional codes
// can be added here; a code stays active for as long as it is present in this
// map. No datastore is involved.
var promoCodes = map[string]float64{
	"50OFF": 0.50,
}

const promoNanosMod = 1000000000

// normalizePromoCode trims surrounding whitespace and upper-cases a code so that
// lookups are case-insensitive.
func normalizePromoCode(code string) string {
	return strings.ToUpper(strings.TrimSpace(code))
}

// promoDiscountRate returns the discount rate for a code and whether the code is
// recognised.
func promoDiscountRate(code string) (float64, bool) {
	rate, ok := promoCodes[normalizePromoCode(code)]
	return rate, ok
}

// discountAmount returns the portion of m to deduct for the given rate,
// preserving the units/nanos money representation and the currency of m.
func discountAmount(m pb.Money, rate float64) pb.Money {
	totalNanos := m.GetUnits()*promoNanosMod + int64(m.GetNanos())
	discountNanos := int64(float64(totalNanos) * rate)
	return pb.Money{
		CurrencyCode: m.GetCurrencyCode(),
		Units:        discountNanos / promoNanosMod,
		Nanos:        int32(discountNanos % promoNanosMod),
	}
}
