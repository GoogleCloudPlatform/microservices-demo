package main

import (
	"math"

	pb "./genproto"
)

func sum(m1, m2 pb.MoneyAmount) pb.MoneyAmount {
	f1, f2 := float64(m1.Fractional), float64(m2.Fractional)
	lg1 := math.Max(1, math.Ceil(math.Log10(f1)))
	lg2 := math.Max(1, math.Ceil(math.Log10(f2)))
	lgMax := math.Max(lg1, lg2)

	dSum := m1.Decimal + m2.Decimal
	o1 := f1 * math.Pow(10, lgMax-lg1)
	o2 := f2 * math.Pow(10, lgMax-lg2)
	fSum := o1 + o2
	if fSum >= math.Pow(10, lgMax) {
		fSum -= math.Pow(10, lgMax)
		dSum++
	}

	for int(fSum)%10 == 0 && fSum != 0 {
		fSum = float64(int(fSum) / 10)
	}

	return pb.MoneyAmount{
		Decimal:    dSum,
		Fractional: uint32(fSum)}
}

func sumMoney(m1, m2 pb.Money) pb.Money {
	s := sum(*m1.Amount, *m2.Amount)
	return pb.Money{
		Amount:       &s,
		CurrencyCode: m1.CurrencyCode}
}
