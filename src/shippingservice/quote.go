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
	var p float64 = 1 + (count64 * 0.2)
	return count64 + math.Pow(3, p)
}
