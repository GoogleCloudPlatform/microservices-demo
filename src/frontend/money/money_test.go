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

package money

import (
	"fmt"
	"reflect"
	"testing"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"
)

func mmc(u int64, n int32, c string) pb.Money { return pb.Money{Units: u, Nanos: n, CurrencyCode: c} }
func mm(u int64, n int32) pb.Money            { return mmc(u, n, "") }

func TestIsValid(t *testing.T) {
	tests := []struct {
		name string
		in   pb.Money
		want bool
	}{
		{"valid -/-", mm(-981273891273, -999999999), true},
		{"invalid -/+", mm(-981273891273, +999999999), false},
		{"valid +/+", mm(981273891273, 999999999), true},
		{"invalid +/-", mm(981273891273, -999999999), false},
		{"invalid +/+overflow", mm(3, 1000000000), false},
		{"invalid +/-overflow", mm(3, -1000000000), false},
		{"invalid -/+overflow", mm(-3, 1000000000), false},
		{"invalid -/-overflow", mm(-3, -1000000000), false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := IsValid(tt.in); got != tt.want {
				t.Errorf("IsValid(%v) = %v, want %v", tt.in, got, tt.want)
			}
		})
	}
}

func TestIsZero(t *testing.T) {
	tests := []struct {
		name string
		in   pb.Money
		want bool
	}{
		{"zero", mm(0, 0), true},
		{"not-zero (-/+)", mm(-1, +1), false},
		{"not-zero (-/-)", mm(-1, -1), false},
		{"not-zero (+/+)", mm(+1, +1), false},
		{"not-zero (+/-)", mm(+1, -1), false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := IsZero(tt.in); got != tt.want {
				t.Errorf("IsZero(%v) = %v, want %v", tt.in, got, tt.want)
			}
		})
	}
}

func TestIsPositive(t *testing.T) {
	tests := []struct {
		name string
		in   pb.Money
		want bool
	}{
		{"zero", mm(0, 0), false},
		{"positive (+/+)", mm(+1, +1), true},
		{"invalid (-/+)", mm(-1, +1), false},
		{"negative (-/-)", mm(-1, -1), false},
		{"invalid (+/-)", mm(+1, -1), false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := IsPositive(tt.in); got != tt.want {
				t.Errorf("IsPositive(%v) = %v, want %v", tt.in, got, tt.want)
			}
		})
	}
}

func TestIsNegative(t *testing.T) {
	tests := []struct {
		name string
		in   pb.Money
		want bool
	}{
		{"zero", mm(0, 0), false},
		{"positive (+/+)", mm(+1, +1), false},
		{"invalid (-/+)", mm(-1, +1), false},
		{"negative (-/-)", mm(-1, -1), true},
		{"invalid (+/-)", mm(+1, -1), false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := IsNegative(tt.in); got != tt.want {
				t.Errorf("IsNegative(%v) = %v, want %v", tt.in, got, tt.want)
			}
		})
	}
}

func TestAreSameCurrency(t *testing.T) {
	type args struct {
		l pb.Money
		r pb.Money
	}
	tests := []struct {
		name string
		args args
		want bool
	}{
		{"both empty currency", args{mmc(1, 0, ""), mmc(2, 0, "")}, false},
		{"left empty currency", args{mmc(1, 0, ""), mmc(2, 0, "USD")}, false},
		{"right empty currency", args{mmc(1, 0, "USD"), mmc(2, 0, "")}, false},
		{"mismatching", args{mmc(1, 0, "USD"), mmc(2, 0, "CAD")}, false},
		{"matching", args{mmc(1, 0, "USD"), mmc(2, 0, "USD")}, true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := AreSameCurrency(tt.args.l, tt.args.r); got != tt.want {
				t.Errorf("AreSameCurrency([%v],[%v]) = %v, want %v", tt.args.l, tt.args.r, got, tt.want)
			}
		})
	}
}

func TestAreEquals(t *testing.T) {
	type args struct {
		l pb.Money
		r pb.Money
	}
	tests := []struct {
		name string
		args args
		want bool
	}{
		{"equals", args{mmc(1, 2, "USD"), mmc(1, 2, "USD")}, true},
		{"mismatching currency", args{mmc(1, 2, "USD"), mmc(1, 2, "CAD")}, false},
		{"mismatching units", args{mmc(10, 20, "USD"), mmc(1, 20, "USD")}, false},
		{"mismatching nanos", args{mmc(1, 2, "USD"), mmc(1, 20, "USD")}, false},
		{"negated", args{mmc(1, 2, "USD"), mmc(-1, -2, "USD")}, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := AreEquals(tt.args.l, tt.args.r); got != tt.want {
				t.Errorf("AreEquals([%v],[%v]) = %v, want %v", tt.args.l, tt.args.r, got, tt.want)
			}
		})
	}
}

func TestNegate(t *testing.T) {
	tests := []struct {
		name string
		in   pb.Money
		want pb.Money
	}{
		{"zero", mm(0, 0), mm(0, 0)},
		{"negative", mm(-1, -200), mm(1, 200)},
		{"positive", mm(1, 200), mm(-1, -200)},
		{"carries currency code", mmc(0, 0, "XXX"), mmc(0, 0, "XXX")},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Negate(tt.in); !AreEquals(got, tt.want) {
				t.Errorf("Negate([%v]) = %v, want %v", tt.in, got, tt.want)
			}
		})
	}
}

func TestMust_pass(t *testing.T) {
	v := Must(mm(2, 3), nil)
	if !AreEquals(v, mm(2, 3)) {
		t.Errorf("returned the wrong value: %v", v)
	}
}

func TestMust_panic(t *testing.T) {
	defer func() {
		if r := recover(); r != nil {
			t.Logf("panic captured: %v", r)
		}
	}()
	Must(mm(2, 3), fmt.Errorf("some error"))
	t.Fatal("this should not have executed due to the panic above")
}

func TestSum(t *testing.T) {
	type args struct {
		l pb.Money
		r pb.Money
	}
	tests := []struct {
		name    string
		args    args
		want    pb.Money
		wantErr error
	}{
		{"0+0=0", args{mm(0, 0), mm(0, 0)}, mm(0, 0), nil},
		{"Error: currency code on left", args{mmc(0, 0, "XXX"), mm(0, 0)}, mm(0, 0), ErrMismatchingCurrency},
		{"Error: currency code on right", args{mm(0, 0), mmc(0, 0, "YYY")}, mm(0, 0), ErrMismatchingCurrency},
		{"Error: currency code mismatch", args{mmc(0, 0, "AAA"), mmc(0, 0, "BBB")}, mm(0, 0), ErrMismatchingCurrency},
		{"Error: invalid +/-", args{mm(+1, -1), mm(0, 0)}, mm(0, 0), ErrInvalidValue},
		{"Error: invalid -/+", args{mm(0, 0), mm(-1, +2)}, mm(0, 0), ErrInvalidValue},
		{"Error: invalid nanos", args{mm(0, 1000000000), mm(1, 0)}, mm(0, 0), ErrInvalidValue},
		{"both positive (no carry)", args{mm(2, 200000000), mm(2, 200000000)}, mm(4, 400000000), nil},
		{"both positive (nanos=max)", args{mm(2, 111111111), mm(2, 888888888)}, mm(4, 999999999), nil},
		{"both positive (carry)", args{mm(2, 200000000), mm(2, 900000000)}, mm(5, 100000000), nil},
		{"both negative (no carry)", args{mm(-2, -200000000), mm(-2, -200000000)}, mm(-4, -400000000), nil},
		{"both negative (carry)", args{mm(-2, -200000000), mm(-2, -900000000)}, mm(-5, -100000000), nil},
		{"mixed (larger positive, just decimals)", args{mm(11, 0), mm(-2, 0)}, mm(9, 0), nil},
		{"mixed (larger negative, just decimals)", args{mm(-11, 0), mm(2, 0)}, mm(-9, 0), nil},
		{"mixed (larger positive, no borrow)", args{mm(11, 100000000), mm(-2, -100000000)}, mm(9, 0), nil},
		{"mixed (larger positive, with borrow)", args{mm(11, 100000000), mm(-2, -9000000 /*.09*/)}, mm(9, 91000000 /*.091*/), nil},
		{"mixed (larger negative, no borrow)", args{mm(-11, -100000000), mm(2, 100000000)}, mm(-9, 0), nil},
		{"mixed (larger negative, with borrow)", args{mm(-11, -100000000), mm(2, 9000000 /*.09*/)}, mm(-9, -91000000 /*.091*/), nil},
		{"0+negative", args{mm(0, 0), mm(-2, -100000000)}, mm(-2, -100000000), nil},
		{"negative+0", args{mm(-2, -100000000), mm(0, 0)}, mm(-2, -100000000), nil},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := Sum(tt.args.l, tt.args.r)
			if err != tt.wantErr {
				t.Errorf("Sum([%v],[%v]): expected err=\"%v\" got=\"%v\"", tt.args.l, tt.args.r, tt.wantErr, err)
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("Sum([%v],[%v]) = %v, want %v", tt.args.l, tt.args.r, got, tt.want)
			}
		})
	}
}
