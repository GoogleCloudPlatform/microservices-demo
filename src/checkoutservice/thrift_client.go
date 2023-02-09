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

	api "checkoutservice/thriftgo/demo"

	_ "github.com/sirupsen/logrus"
)

func (tc *ThriftClient) GetProduct(product_id string) (*api.Product, error) {
	opt := NewDefaultOption()
	opt.HttpUrl = "/ProductCatalogService"
	client, transport, err := NewThriftClient(tc.ProductCatalogService, opt)
	if err != nil {
		return nil, fmt.Errorf("failed creating productcatalogservice client")
	}

	err = transport.Open()
	if err != nil {
		return nil, fmt.Errorf("failed to open transport %w", err)
	}
	defer transport.Close()
	c := api.NewProductCatalogServiceClient(client)
	ctx := context.TODO()
	p, err := c.GetProduct(ctx, product_id)
	if err != nil {
		return nil, err
	}
	return p, nil
}
func (tc *ThriftClient) GetCart(userID string) (*api.Cart, error) {
	opt := NewDefaultOption()
	opt.HttpUrl = "/CartService"
	client, transport, err := NewThriftClient(tc.CartService, opt)
	if err != nil {
		return nil, fmt.Errorf("failed creating cartservice client")
	}
	err = transport.Open()
	if err != nil {
		return nil, fmt.Errorf("failed to open transport %w", err)
	}
	defer transport.Close()
	c := api.NewCartServiceClient(client)
	cart, err := c.GetCart(context.Background(), userID)
	if err != nil {
		return nil, fmt.Errorf("failed calling thrift API GetCart()")
	}
	return cart, nil
}

// ------- Payment Service
// ------- Shipping Service
func (tc *ThriftClient) SendOrderConfirmation(ctx context.Context, address string, items *api.OrderResult_) error {
	opt := NewDefaultOption()
	opt.HttpTransport = true
	opt.HttpUrl = "/Emailservice"

	client, transport, err := NewThriftClient(tc.Emailservice, opt)
	if err != nil {
		return fmt.Errorf("failed email client")
	}

	err = transport.Open()
	if err != nil {
		return fmt.Errorf("failed to open transport %w", err)
	}
	defer transport.Close()
	c := api.NewEmailServiceClient(client)
	if err := c.SendOrderConfirmation(ctx, address, items); err != nil {
		return err
	}
	return nil
}

// ------- Email
func (tc *ThriftClient) ShipOrder(ctx context.Context, address *api.Address, items []*api.CartItem) error {
	opt := NewDefaultOption()
	opt.HttpTransport = true
	opt.HttpUrl = "/ShippingService"

	client, transport, err := NewThriftClient(tc.Shippingservice, opt)
	if err != nil {
		return fmt.Errorf("failed creating ShippingService client")
	}
	err = transport.Open()
	if err != nil {
		return fmt.Errorf("failed to open transport %w", err)
	}
	defer transport.Close()
	_ = client
	return nil
}
