// Copyright 2022 Skyramp, Inc.
//
//	Licensed under the Apache License, Version 2.0 (the "License");
//	you may not use this file except in compliance with the License.
//	You may obtain a copy of the License at
//
//	http://www.apache.org/licenses/LICENSE-2.0
//
//	Unless required by applicable law or agreed to in writing, software
//	distributed under the License is distributed on an "AS IS" BASIS,
//	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//	See the License for the specific language governing permissions and
//	limitations under the License.

package main

import (
	"context"
	"fmt"
	"shippingservice/thriftgo/demo"
)

type Handler struct{}

func (h *Handler) GetQuote(ctx context.Context, address *demo.Address, items []*demo.CartItem) (*demo.Money, error) {
	log.Info("[GetQuote] received request")
	defer log.Info("[GetQuote] completed request")

	// 1. Generate a quote based on the total number of items to be shipped.
	quote := CreateQuoteFromCount(0)
	return &demo.Money{
		CurrencyCode: "USD",
		Units:        int64(quote.Dollars),
		Nanos:        int32(quote.Cents * 10000000),
	}, nil
}

func (h *Handler) ShipOrder(ctx context.Context, address *demo.Address, items []*demo.CartItem) (string, error) {
	log.Info("[ShipOrder] received request")
	defer log.Info("[ShipOrder] completed request")
	// 1. Create a Tracking ID
	baseAddress := fmt.Sprintf("%s, %s, %s", address.StreetAddress, address.City, address.State)
	id := CreateTrackingId(baseAddress)

	return CreateTrackingId(id), nil
}

func startThrift(port string, opt *Option) {
	processor := demo.NewShippingServiceProcessor(&Handler{})
	go func() {
		if opt.HttpTransport {
			NewHttpThriftServer(fmt.Sprintf("0.0.0.0:%s", port), opt, processor)
		} else {
			NewStandardThriftServer(fmt.Sprintf("0.0.0.0:%s", port), opt, processor)
		}
		log.Info("Trift server terminated")
	}()
}
