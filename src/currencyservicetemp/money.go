package main

import (
	"fmt"
	"math"
	"strconv"
	"strings"

	pb "./genproto"
)

func convert(m pb.MoneyAmount, rate float64) pb.MoneyAmount {
	d, f := m.Decimal, m.Fractional
	lg := int(math.Max(1, math.Ceil(math.Log10(float64(f)))))
	ff, _ := strconv.ParseFloat(fmt.Sprintf("%d.%d", d, f), 64)
	res := ff * rate
	resTxt := fmt.Sprintf("%."+strconv.Itoa(lg)+"f", res)
	p := strings.Split(resTxt, ".")

	ds, fs := p[0], p[1]
	fs = strings.TrimSuffix(fs, "0")
	if fs == "" {
		fs = "0"
	}
	dn, _ := strconv.Atoi(ds)
	fn, _ := strconv.Atoi(fs)

	return pb.MoneyAmount{Decimal: uint32(dn), Fractional: uint32(fn)}
}
