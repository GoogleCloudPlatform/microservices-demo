package main

import (
	"reflect"
	"testing"

	pb "./genproto"
)

func Test_sum(t *testing.T) {
	type args struct {
		m1 pb.MoneyAmount
		m2 pb.MoneyAmount
	}
	tests := []struct {
		name string
		args args
		want pb.MoneyAmount
	}{
		{
			name: "no fractions",
			args: args{pb.MoneyAmount{Decimal: 10}, pb.MoneyAmount{Decimal: 100}},
			want: pb.MoneyAmount{Decimal: 110},
		},
		{
			name: "same fraction digits",
			args: args{pb.MoneyAmount{Decimal: 1, Fractional: 23}, pb.MoneyAmount{Decimal: 1, Fractional: 44}},
			want: pb.MoneyAmount{Decimal: 2, Fractional: 67},
		},
		{
			name: "different fraction digits",
			args: args{pb.MoneyAmount{Decimal: 1, Fractional: 351}, pb.MoneyAmount{Decimal: 1, Fractional: 1}},
			want: pb.MoneyAmount{Decimal: 2, Fractional: 451},
		},
		{
			name: "redundant trailing zeroes are removed from fraction",
			args: args{pb.MoneyAmount{Decimal: 1, Fractional: 351}, pb.MoneyAmount{Decimal: 1, Fractional: 349}},
			want: pb.MoneyAmount{Decimal: 2, Fractional: 7},
		},
		{
			name: "carry",
			args: args{pb.MoneyAmount{Decimal: 1, Fractional: 5}, pb.MoneyAmount{Decimal: 1, Fractional: 5000000}},
			want: pb.MoneyAmount{Decimal: 3},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := sum(tt.args.m1, tt.args.m2); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("sum(%v+%v) = %v, want=%v", tt.args.m1, tt.args.m2, got, tt.want)
			}
		})
	}
}
