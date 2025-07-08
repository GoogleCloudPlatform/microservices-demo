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

package main

import (
	"context"
	"time"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"

	"github.com/pkg/errors"
)

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

const (
	avoidNoopCurrencyConversionRPC = false
)

func getCurrencyServiceRestAddr() string {
	addr := os.Getenv("CURRENCY_SERVICE_REST_ADDR")
	if addr == "" {
		// Default to localhost if not set, for local development
		// In a real deployment, this should be configured properly.
		return "http://localhost:7000"
	}
	return addr
}

func (fe *frontendServer) getCurrenciesRest(ctx context.Context) ([]string, error) {
	url := fmt.Sprintf("%s/currencies", getCurrencyServiceRestAddr())
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, errors.Wrap(err, "failed to create getCurrencies request")
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, errors.Wrap(err, "failed to call getCurrencies endpoint")
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := ioutil.ReadAll(resp.Body)
		return nil, fmt.Errorf("getCurrencies failed with status %d: %s", resp.StatusCode, string(bodyBytes))
	}

	var currencyCodes []string
	if err := json.NewDecoder(resp.Body).Decode(&currencyCodes); err != nil {
		return nil, errors.Wrap(err, "failed to decode getCurrencies response")
	}

	var out []string
	for _, c := range currencyCodes {
		if _, ok := whitelistedCurrencies[c]; ok {
			out = append(out, c)
		}
	}
	return out, nil
}

// getCurrencies keeps the same signature and now calls the REST version.
func (fe *frontendServer) getCurrencies(ctx context.Context) ([]string, error) {
	// Original gRPC call:
	// currs, err := pb.NewCurrencyServiceClient(fe.currencySvcConn).
	// 	GetSupportedCurrencies(ctx, &pb.Empty{})
	// if err != nil {
	// 	return nil, err
	// }
	// var out []string
	// for _, c := range currs.CurrencyCodes {
	// 	if _, ok := whitelistedCurrencies[c]; ok {
	// 		out = append(out, c)
	// 	}
	// }
	// return out, nil
	return fe.getCurrenciesRest(ctx)
}

func (fe *frontendServer) getProducts(ctx context.Context) ([]*pb.Product, error) {
	resp, err := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		ListProducts(ctx, &pb.Empty{})
	return resp.GetProducts(), err
}

func (fe *frontendServer) getProduct(ctx context.Context, id string) (*pb.Product, error) {
	resp, err := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		GetProduct(ctx, &pb.GetProductRequest{Id: id})
	return resp, err
}

func (fe *frontendServer) getCart(ctx context.Context, userID string) ([]*pb.CartItem, error) {
	resp, err := pb.NewCartServiceClient(fe.cartSvcConn).GetCart(ctx, &pb.GetCartRequest{UserId: userID})
	return resp.GetItems(), err
}

func (fe *frontendServer) emptyCart(ctx context.Context, userID string) error {
	_, err := pb.NewCartServiceClient(fe.cartSvcConn).EmptyCart(ctx, &pb.EmptyCartRequest{UserId: userID})
	return err
}

func (fe *frontendServer) insertCart(ctx context.Context, userID, productID string, quantity int32) error {
	_, err := pb.NewCartServiceClient(fe.cartSvcConn).AddItem(ctx, &pb.AddItemRequest{
		UserId: userID,
		Item: &pb.CartItem{
			ProductId: productID,
			Quantity:  quantity},
	})
	return err
}

// CurrencyConversionRequest mirrors the pb.CurrencyConversionRequest for REST
type CurrencyConversionRequest struct {
	From   *pb.Money `json:"from"`
	ToCode string    `json:"to_code"`
}

func (fe *frontendServer) convertCurrencyRest(ctx context.Context, money *pb.Money, toCurrencyCode string) (*pb.Money, error) {
	if avoidNoopCurrencyConversionRPC && money.GetCurrencyCode() == toCurrencyCode {
		return money, nil
	}

	url := fmt.Sprintf("%s/convert", getCurrencyServiceRestAddr())
	reqBody := CurrencyConversionRequest{
		From:   money,
		ToCode: toCurrencyCode,
	}
	jsonBody, err := json.Marshal(reqBody)
	if err != nil {
		return nil, errors.Wrap(err, "failed to marshal convertCurrency request body")
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(jsonBody))
	if err != nil {
		return nil, errors.Wrap(err, "failed to create convertCurrency request")
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, errors.Wrap(err, "failed to call convertCurrency endpoint")
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := ioutil.ReadAll(resp.Body)
		return nil, fmt.Errorf("convertCurrency failed with status %d: %s", resp.StatusCode, string(bodyBytes))
	}

	var convertedMoney pb.Money
	if err := json.NewDecoder(resp.Body).Decode(&convertedMoney); err != nil {
		return nil, errors.Wrap(err, "failed to decode convertCurrency response")
	}
	return &convertedMoney, nil
}

// convertCurrency keeps the same signature and now calls the REST version.
func (fe *frontendServer) convertCurrency(ctx context.Context, money *pb.Money, currency string) (*pb.Money, error) {
	// Original gRPC call:
	// if avoidNoopCurrencyConversionRPC && money.GetCurrencyCode() == currency {
	// 	return money, nil
	// }
	// return pb.NewCurrencyServiceClient(fe.currencySvcConn).
	// 	Convert(ctx, &pb.CurrencyConversionRequest{
	// 		From:   money,
	// 		ToCode: currency})
	return fe.convertCurrencyRest(ctx, money, currency)
}

func (fe *frontendServer) getShippingQuote(ctx context.Context, items []*pb.CartItem, currency string) (*pb.Money, error) {
	quote, err := pb.NewShippingServiceClient(fe.shippingSvcConn).GetQuote(ctx,
		&pb.GetQuoteRequest{
			Address: nil,
			Items:   items})
	if err != nil {
		return nil, err
	}
	localized, err := fe.convertCurrency(ctx, quote.GetCostUsd(), currency)
	return localized, errors.Wrap(err, "failed to convert currency for shipping cost")
}

func (fe *frontendServer) getRecommendations(ctx context.Context, userID string, productIDs []string) ([]*pb.Product, error) {
	resp, err := pb.NewRecommendationServiceClient(fe.recommendationSvcConn).ListRecommendations(ctx,
		&pb.ListRecommendationsRequest{UserId: userID, ProductIds: productIDs})
	if err != nil {
		return nil, err
	}
	out := make([]*pb.Product, len(resp.GetProductIds()))
	for i, v := range resp.GetProductIds() {
		p, err := fe.getProduct(ctx, v)
		if err != nil {
			return nil, errors.Wrapf(err, "failed to get recommended product info (#%s)", v)
		}
		out[i] = p
	}
	if len(out) > 4 {
		out = out[:4] // take only first four to fit the UI
	}
	return out, err
}

func (fe *frontendServer) getAd(ctx context.Context, ctxKeys []string) ([]*pb.Ad, error) {
	ctx, cancel := context.WithTimeout(ctx, time.Millisecond*100)
	defer cancel()

	resp, err := pb.NewAdServiceClient(fe.adSvcConn).GetAds(ctx, &pb.AdRequest{
		ContextKeys: ctxKeys,
	})
	return resp.GetAds(), errors.Wrap(err, "failed to get ads")
}
