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
	"google.golang.org/grpc/status"

	"github.com/pkg/errors"
)

const (
	avoidNoopCurrencyConversionRPC = false
)

func (fe *frontendServer) getCurrencies(ctx context.Context) ([]string, error) {
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, CURRENCYSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	currs, err := pb.NewCurrencyServiceClient(fe.currencySvcConn).
		GetSupportedCurrencies(newCtx, &pb.Empty{})
	if err != nil {
		return nil, err
	}

	// Check gRPC reply
	checkResponse(status.Code(err), CURRENCYSERVICE, RequestID, err)

	var out []string
	for _, c := range currs.CurrencyCodes {
		if _, ok := whitelistedCurrencies[c]; ok {
			out = append(out, c)
		}
	}
	return out, nil
}

func (fe *frontendServer) getProducts(ctx context.Context) ([]*pb.Product, error) {
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, PRODUCTCATALOGSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	resp, err := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		ListProducts(newCtx, &pb.Empty{})

	// Check gRPC reply
	checkResponse(status.Code(err), PRODUCTCATALOGSERVICE, RequestID, err)

	return resp.GetProducts(), err
}

func (fe *frontendServer) getProduct(ctx context.Context, id string) (*pb.Product, error) {
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, PRODUCTCATALOGSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	resp, err := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		GetProduct(newCtx, &pb.GetProductRequest{Id: id})

	// Check gRPC reply
	checkResponse(status.Code(err), PRODUCTCATALOGSERVICE, RequestID, err)

	return resp, err
}

func (fe *frontendServer) getCart(ctx context.Context, userID string) ([]*pb.CartItem, error) {
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, CARTSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	resp, err := pb.NewCartServiceClient(fe.cartSvcConn).GetCart(newCtx, &pb.GetCartRequest{UserId: userID})

	// Check gRPC reply
	checkResponse(status.Code(err), CARTSERVICE, RequestID, err)

	return resp.GetItems(), err
}

func (fe *frontendServer) emptyCart(ctx context.Context, userID string) error {
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, CARTSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	_, err := pb.NewCartServiceClient(fe.cartSvcConn).EmptyCart(newCtx, &pb.EmptyCartRequest{UserId: userID})

	// Check gRPC reply
	checkResponse(status.Code(err), CARTSERVICE, RequestID, err)

	return err
}

func (fe *frontendServer) insertCart(ctx context.Context, userID, productID string, quantity int32) error {
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, CARTSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	_, err := pb.NewCartServiceClient(fe.cartSvcConn).AddItem(newCtx, &pb.AddItemRequest{
		UserId: userID,
		Item: &pb.CartItem{
			ProductId: productID,
			Quantity:  quantity},
	})

	// Check gRPC reply
	checkResponse(status.Code(err), CARTSERVICE, RequestID, err)

	return err
}

func (fe *frontendServer) convertCurrency(ctx context.Context, money *pb.Money, currency string) (*pb.Money, error) {
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, CURRENCYSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	if avoidNoopCurrencyConversionRPC && money.GetCurrencyCode() == currency {
		return money, nil
	}

	res, err := pb.NewCurrencyServiceClient(fe.currencySvcConn).
		Convert(newCtx, &pb.CurrencyConversionRequest{
			From:   money,
			ToCode: currency})

	// Check gRPC reply
	checkResponse(status.Code(err), CURRENCYSERVICE, RequestID, err)

	return res, nil
}

func (fe *frontendServer) getShippingQuote(ctx context.Context, items []*pb.CartItem, currency string) (*pb.Money, error) {
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, SHIPPINGSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	quote, err := pb.NewShippingServiceClient(fe.shippingSvcConn).GetQuote(newCtx,
		&pb.GetQuoteRequest{
			Address: nil,
			Items:   items})
	if err != nil {
		return nil, err
	}
	// Check gRPC reply
	checkResponse(status.Code(err), SHIPPINGSERVICE, RequestID, err)

	localized, err := fe.convertCurrency(ctx, quote.GetCostUsd(), currency)
	return localized, errors.Wrap(err, "failed to convert currency for shipping cost")
}

func (fe *frontendServer) getRecommendations(ctx context.Context, userID string, productIDs []string) ([]*pb.Product, error) {
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, RECOMMENDATIONSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	resp, err := pb.NewRecommendationServiceClient(fe.recommendationSvcConn).ListRecommendations(newCtx,
		&pb.ListRecommendationsRequest{UserId: userID, ProductIds: productIDs})
	if err != nil {
		return nil, err
	}

	// Check gRPC reply
	checkResponse(status.Code(err), RECOMMENDATIONSERVICE, RequestID, err)

	out := make([]*pb.Product, len(resp.GetProductIds()))
	for i, v := range resp.GetProductIds() {
		p, err := fe.getProduct(newCtx, v)
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
	// Prepare metadata and set timeout
	metadataCtx, RequestID := setMetadata(ctx, FRONTEND, ADSERVICE)
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	resp, err := pb.NewAdServiceClient(fe.adSvcConn).GetAds(newCtx, &pb.AdRequest{
		ContextKeys: ctxKeys,
	})

	// Check gRPC reply
	checkResponse(status.Code(err), ADSERVICE, RequestID, err)

	return resp.GetAds(), errors.Wrap(err, "failed to get ads")
}
