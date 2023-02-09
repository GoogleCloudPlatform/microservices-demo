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

type Address struct {
	StreetAddress string `json:"street_address,omitempty"`
	City          string `json:"city,omitempty"`
	State         string `json:"state,omitempty"`
	Country       string `json:"country,omitempty"`
	ZipCode       int32  `json:"zip_code,omitempty"`
}

type Money struct {
	CurrencyCode string `json:"currency_code,omitempty"`
	Units        int64  `json:"units,omitempty"`
	Nanos        int32  `json:"nanos,omitempty"`
}
type Product struct {
	Id          string   `json:"id,omitempty"`
	Name        string   `json:"name,omitempty"`
	Description string   `json:"description,omitempty"`
	Picture     string   `json:"picture,omitempty"`
	PriceUsd    Money    `json:"priceUsd,omitempty"`
	Categories  []string `json:"categories,omitempty"`
}

type CreditCardInfo struct {
	CreditCardNumber          string `json:"credit_card_number,omitempty"`
	CreditCardCvv             int32  `json:"credit_card_cvv,omitempty"`
	CreditCardExpirationYear  int32  `json:"credit_card_expiration_year,omitempty"`
	CreditCardExpirationMonth int32  `json:"credit_card_expiration_month,omitempty"`
}

type CartItem struct {
	ProductId string `json:"product_id,omitempty"`
	Quantity  int32  `json:"quantity,omitempty"`
}

type Cart struct {
	UserId string      `json:"user_id,omitempty"`
	Items  []*CartItem `json:"items,omitempty"`
}

type OrderItem struct {
	Item *CartItem `json:"item,omitempty"`
	Cost *Money    `json:"cost,omitempty"`
}

type OrderResult struct {
	OrderId            string       `json:"order_id,omitempty"`
	ShippingTrackingId string       `json:"shipping_tracking_id,omitempty"`
	ShippingCost       *Money       `json:"shipping_cost,omitempty"`
	ShippingAddress    *Address     `json:"shipping_address,omitempty"`
	Items              []*OrderItem `json:"items,omitempty"`
}

type PlaceOrderRequest struct {
	UserId       string          `json:"user_id,omitempty"`
	UserCurrency string          `json:"user_currency,omitempty"`
	Address      *Address        `json:"address,omitempty"`
	Email        string          `json:"email,omitempty"`
	CreditCard   *CreditCardInfo `json:"credit_card,omitempty"`
}

type AdRequest struct {
	ContextKeys []string `json:"context_keys,omitempty"`
}

type Ad struct {
	RedirectUrl string `json:"redirect_url,omitempty"`
	Text        string `json:"text,omitempty"`
}

type ShipOrderRequest struct {
	Address *Address    `json:"address,omitempty"`
	Items   []*CartItem `json:"items,omitempty"`
}

type ShipOrderResponse struct {
	TrackingId string `json:"tracking_id,omitempty"`
}

