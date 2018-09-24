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
	"math"
)

// Quote represents a currency value.
type Quote struct {
	Dollars uint32
	Cents   uint32
}

// String representation of the Quote.
func (q Quote) String() string {
	return fmt.Sprintf("$%d.%d", q.Dollars, q.Cents)
}

// CreateQuoteFromCount takes a number of items and returns a Price struct.
func CreateQuoteFromCount(count int) Quote {
	return CreateQuoteFromFloat(quoteByCountFloat(count))
}

// CreateQuoteFromFloat takes a price represented as a float and creates a Price struct.
func CreateQuoteFromFloat(value float64) Quote {
	units, fraction := math.Modf(value)
	return Quote{
		uint32(units),
		uint32(math.Trunc(fraction * 100)),
	}
}

// quoteByCountFloat takes a number of items and generates a price quote represented as a float.
func quoteByCountFloat(count int) float64 {
	if count == 0 {
		return 0
	}
	count64 := float64(count)
	var p = 1 + (count64 * 0.2)
	return count64 + math.Pow(3, p)
}
