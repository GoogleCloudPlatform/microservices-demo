package main

import (
	"math"

	pb "frontend/genproto"
)

// TODO(ahmetb): any logic below is flawed because I just realized we have no
// way of representing amounts like 17.07 because Fractional cannot store 07.
func multMoney(m pb.MoneyAmount, n uint32) pb.MoneyAmount {
	out := m
	for n > 1 {
		out = sum(out, m)
		n--
	}
	return out
}

func sum(m1, m2 pb.MoneyAmount) pb.MoneyAmount {
	// TODO(ahmetb) this is copied from ./checkoutservice/money.go, find a
	// better mult function.
	f1, f2 := float64(m1.Fractional), float64(m2.Fractional)
	lg1 := math.Max(1, math.Ceil(math.Log10(f1)))
	if f1 == math.Pow(10, lg1) {
		lg1++
	}
	lg2 := math.Max(1, math.Ceil(math.Log10(f2)))
	if f2 == math.Pow(10, lg2) {
		lg2++
	}
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
