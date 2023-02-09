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
	thrift "cartservice/thriftgo/demo"
	"context"
	"fmt"
)

type Handler struct{}

func (h Handler) AddItem(ctx context.Context, user_id string, item *thrift.CartItem) (_err error) {
	log.Debugf("calling thrift api AddItem() for user id [%s] product id [%s] quantity [%d]", user_id, item.GetProductID(), item.GetQuantity())
	AddItem(user_id, item.GetProductID(), int32(item.GetQuantity()))
	return nil
}

func (h Handler) GetCart(ctx context.Context, user_id string) (*thrift.Cart, error) {
	log.Debugf("calling thrift api GetCart() for user id [%s]", user_id)
	cart := GetCart(user_id)
	cartItems := make([]*thrift.CartItem, 0, len(cart.Items))
	for _, item := range cart.Items {
		c := thrift.CartItem{ProductID: item.ProductId, Quantity: item.Quantity}
		cartItems = append(cartItems, &c)
	}
	return &thrift.Cart{
		UserID: user_id,
		Items:  cartItems,
	}, nil
}

func (h Handler) EmptyCart(ctx context.Context, user_id string) error {
	log.Debugf("calling thrift api EmptyCart() for user id [%s]", user_id)
	EmtyCart(user_id)
	return nil
}

func runThrift(port string) {
	processor := thrift.NewCartServiceProcessor(&Handler{})
	go func() {
		opt := NewDefaultOption()
		opt.HttpUrl = "/CartService"
		hostPort := fmt.Sprintf("0.0.0.0:%s", port)
		NewHttpThriftServer(hostPort, opt, processor)
	}()
}
