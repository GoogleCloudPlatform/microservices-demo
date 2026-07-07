package main

import (
	"testing"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice/genproto"
	money "github.com/GoogleCloudPlatform/microservices-demo/src/checkoutservice/money"
)

func TestFixedAmountUsesRequestedCurrency(t *testing.T) {
	got := fixedAmount("JPY", 10)

	if got.GetCurrencyCode() != "JPY" {
		t.Fatalf("fixedAmount() currency = %q, want %q", got.GetCurrencyCode(), "JPY")
	}
	if got.GetUnits() != 10 {
		t.Fatalf("fixedAmount() units = %d, want %d", got.GetUnits(), 10)
	}
	if got.GetNanos() != 0 {
		t.Fatalf("fixedAmount() nanos = %d, want %d", got.GetNanos(), 0)
	}
}

func TestSave10DiscountIsNotConvertedForJPY(t *testing.T) {
	total := pb.Money{CurrencyCode: "JPY", Units: 13303, Nanos: 26978997}
	discount := *fixedAmount("JPY", coupons["SAVE10"])

	newTotal, err := money.Sum(total, money.Negate(discount))
	if err != nil {
		t.Fatalf("money.Sum() error = %v", err)
	}

	if discount.GetCurrencyCode() != "JPY" {
		t.Fatalf("discount currency = %q, want %q", discount.GetCurrencyCode(), "JPY")
	}
	if discount.GetUnits() != 10 || discount.GetNanos() != 0 {
		t.Fatalf("discount = %d.%09d, want 10.000000000", discount.GetUnits(), discount.GetNanos())
	}
	if newTotal.GetCurrencyCode() != "JPY" {
		t.Fatalf("newTotal currency = %q, want %q", newTotal.GetCurrencyCode(), "JPY")
	}
	if newTotal.GetUnits() != 13293 || newTotal.GetNanos() != 26978997 {
		t.Fatalf("newTotal = %d.%09d, want 13293.026978997", newTotal.GetUnits(), newTotal.GetNanos())
	}
}
