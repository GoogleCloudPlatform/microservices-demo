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
	thrift "checkoutservice/thriftgo/demo"
	"context"
	"fmt"
	"os"

	"github.com/google/uuid"
)

type ThriftClient struct {
	CartService           string
	ProductCatalogService string
	Shippingservice       string
	Currencyservice       string
	Paymentservice        string
	Emailservice          string
}

var thriftClient = &ThriftClient{}

type Handler struct{}

func init() {
	log.Info("entering thrift.init()")
	thriftClient.CartService = getService(CART_SERVICE_ADDR, 50000)
	thriftClient.ProductCatalogService = getService(PRODUCT_CATALOG_SERVICE_ADDR, 50000)
	thriftClient.Currencyservice = getService(CURRENCY_SERVICE_ADDR, 50000)
	thriftClient.Paymentservice = getService(PAYMENT_SERVICE_ADDR, 50000)
	thriftClient.Emailservice = getService(EMAIL_SERVICE_ADDR, 50000)
	thriftClient.Shippingservice = getService(SHIPPING_SERVICE_ADDR, 50000)
}

// PlaceOrder implements demo.CheckoutService
func (*Handler) PlaceOrder(ctx context.Context, user_id string, user_currency string, address *thrift.Address, email string, credit_card *thrift.CreditCardInfo) (_r *thrift.OrderResult_, _err error) {

	result := &thrift.OrderResult_{
		ShippingAddress:    address,
		Items:              make([]*thrift.OrderItem, 0),
		ShippingCost:       &thrift.Money{CurrencyCode: "USD", Units: 10, Nanos: 100},
		ShippingTrackingID: uuid.NewString(),
		OrderID:            uuid.NewString(),
	}
	// Get User Cart
	cart, err := thriftClient.GetCart(user_id)
	if err != nil {
		msg := fmt.Sprintf("failed to get cart for user [%s], err [%v]", user_id, err)
		log.Error(msg)
		return nil, fmt.Errorf(msg)
	}
	// Get Products
	for _, item := range cart.Items {
		if p, err := thriftClient.GetProduct(item.ProductID); err != nil {
			msg := fmt.Sprintf("failed to get product [%s], err [%v]", p.ID, err)
			log.Error(msg)
			return nil, fmt.Errorf(msg)
		} else {
			result.Items = append(result.Items, &thrift.OrderItem{Item: item, Cost: p.PriceUsd})
		}
	}

	return result, nil
}

func startThrift() {
	go func() {
		port := "50000"
		if os.Getenv("THRIFT_PORT") != "" {
			port = os.Getenv("THRIFT_PORT")
		}
		processor := thrift.NewCheckoutServiceProcessor(&Handler{})
		opt := NewDefaultOption()
		opt.HttpUrl = "/CheckoutService"
		hostPort := fmt.Sprintf("0.0.0.0:%s", port)
		NewHttpThriftServer(hostPort, opt, processor)
	}()
}
