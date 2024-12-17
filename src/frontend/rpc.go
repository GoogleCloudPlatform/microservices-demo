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

	"io/ioutil"
	"net/http"
	"encoding/json"
	"github.com/sirupsen/logrus"
	"bytes"
)

const (
	avoidNoopCurrencyConversionRPC = false
)

func (fe *frontendServer) getCurrencies(ctx context.Context) ([]string, error) {
	currs, err := pb.NewCurrencyServiceClient(fe.currencySvcConn).
		GetSupportedCurrencies(ctx, &pb.Empty{})
	if err != nil {
		return nil, err
	}
	var out []string
	for _, c := range currs.CurrencyCodes {
		if _, ok := whitelistedCurrencies[c]; ok {
			out = append(out, c)
		}
	}
	return out, nil
}

func (fe *frontendServer) getLanguages(log logrus.FieldLogger) ([]string, error) {
	resp, err1 := http.Get("http://languageservice:3000/getSupportedLanguages")

	if err1 != nil {
		return nil, err1
	}

	defer resp.Body.Close()
	respBody, err2 := ioutil.ReadAll(resp.Body)

	if err2 != nil {
		return nil, err2
	}

	var body []string
	json.Unmarshal(respBody, &body)

	return body, nil
}

func (fe *frontendServer) getTranslation(translationKey string, languageCode string) (string, error) {

	// url := fmt.Sprintf("http://languageservice:3000/translate?translationKey=%s&targetLanguageCode=%s", translationKey, languageCode)

	// resp, err1 := http.Get(url)

	// if err1 != nil {
	// 	return "", err1
	// }

	// defer resp.Body.Close()

	// body, err2 := ioutil.ReadAll(resp.Body)
	// if err2 != nil {
	// 	return "", err2
	// }

	// sb := string(body)

	// return sb, nil

	postBody, err1 := json.Marshal(map[string]string{
		"translationKey":  translationKey,
		"targetLanguageCode": languageCode,
	 })

	 if err1 != nil {
		return "", err1
	}

	requestBody := bytes.NewBuffer(postBody)

	resp, err2 := http.Post("http://languageservice:3000/translate", "application/json", requestBody)

	if err2 != nil {
		return "", err2
	}

	defer resp.Body.Close()

	body, err3 := ioutil.ReadAll(resp.Body)
	if err3 != nil {
		return "", err3
	}

	sb := string(body)

	return sb, nil
}


func (fe *frontendServer) getProducts(ctx context.Context, langCode string) ([]*pb.Product, error) {
	resp, err := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		ListProducts(ctx, &pb.Empty{})
	products := resp.GetProducts()

	translatedProducts := make([]*pb.Product, len(products))
    for i, product := range products {
  		translatedProducts[i] = product

		nameText, err2 := fe.getTranslation(product.Name, langCode)

		if err2 == nil {
			translatedProducts[i].Name = nameText
		}
	
		descText, err3 := fe.getTranslation(product.Description, langCode)
	
		if err3 == nil {
			translatedProducts[i].Description = descText
		}
    }

    return translatedProducts, err
}

func (fe *frontendServer) getProduct(ctx context.Context, id string, langCode string) (*pb.Product, error) {
	product, err1 := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		GetProduct(ctx, &pb.GetProductRequest{Id: id})

	if err1 != nil {
		return nil, err1
	}

	nameText, err2 := fe.getTranslation(product.Name, langCode)

	if err2 != nil {
		return product, nil
	}

	descText, err3 := fe.getTranslation(product.Description, langCode)

	if err3 != nil {
		return product, nil
	}

	product.Name = nameText
	product.Description = descText

	return product, nil
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

func (fe *frontendServer) convertCurrency(ctx context.Context, money *pb.Money, currency string) (*pb.Money, error) {
	if avoidNoopCurrencyConversionRPC && money.GetCurrencyCode() == currency {
		return money, nil
	}
	return pb.NewCurrencyServiceClient(fe.currencySvcConn).
		Convert(ctx, &pb.CurrencyConversionRequest{
			From:   money,
			ToCode: currency})
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

func (fe *frontendServer) getRecommendations(ctx context.Context, userID string, productIDs []string, langCode string) ([]*pb.Product, error) {
	resp, err := pb.NewRecommendationServiceClient(fe.recommendationSvcConn).ListRecommendations(ctx,
		&pb.ListRecommendationsRequest{UserId: userID, ProductIds: productIDs})
	if err != nil {
		return nil, err
	}
	out := make([]*pb.Product, len(resp.GetProductIds()))
	for i, v := range resp.GetProductIds() {
		p, err := fe.getProduct(ctx, v, langCode)
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
