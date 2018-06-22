package main

import (
	"reflect"
	"testing"

	pb "./genproto"
)

func Test_convert(t *testing.T) {
	type args struct {
		m    pb.MoneyAmount
		rate float64
	}
	tests := []struct {
		name string
		args args
		want pb.MoneyAmount
	}{
		{
			"0.33*3", args{pb.MoneyAmount{Decimal: 0, Fractional: 330}, 3}, pb.MoneyAmount{Decimal: 0, Fractional: 99},
		},
		{
			"10.00*0.5", args{pb.MoneyAmount{Decimal: 10}, 0.5}, pb.MoneyAmount{Decimal: 5},
		},
		{
			"10.00*1.5", args{pb.MoneyAmount{Decimal: 10}, 1.5}, pb.MoneyAmount{Decimal: 15},
		},
		{
			"10.00*1/3", args{pb.MoneyAmount{Decimal: 10}, 1.0 / 3}, pb.MoneyAmount{Decimal: 3, Fractional: 3},
		},
		{
			"32.320*0.5 (trailing zero removed)", args{pb.MoneyAmount{Decimal: 32, Fractional: 32}, 0.5}, pb.MoneyAmount{Decimal: 16, Fractional: 16},
		},
		{
			"33.33*(1/3) (trailing zero removed)", args{pb.MoneyAmount{Decimal: 33, Fractional: 33}, 1.0 / 3}, pb.MoneyAmount{Decimal: 11, Fractional: 11},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := convert(tt.args.m, tt.args.rate); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("convert([%v]*%f) = %v, want=[%v]", tt.args.m, tt.args.rate, got, tt.want)
			}
		})
	}
}
