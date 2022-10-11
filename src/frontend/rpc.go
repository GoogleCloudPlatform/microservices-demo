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
	"github.com/google/uuid"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"

	"github.com/pkg/errors"
)

const (
	avoidNoopCurrencyConversionRPC = false
)

func (fe *frontendServer) getCurrencies(ctx context.Context) ([]string, error) {
	RequestID, err := uuid.NewRandom()

	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	event := "Sending message to " + CURRENCYSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	currs, err := pb.NewCurrencyServiceClient(fe.currencySvcConn).
		GetSupportedCurrencies(newCtx, &pb.Empty{})

	// Check gRPC reply
	checkResponse(status.Code(err), CURRENCYSERVICE, RequestID.String(), err)

	var out []string
	for _, c := range currs.CurrencyCodes {
		if _, ok := whitelistedCurrencies[c]; ok {
			out = append(out, c)
		}
	}
	return out, nil
}

func (fe *frontendServer) getProducts(ctx context.Context) ([]*pb.Product, error) {
	RequestID, err := uuid.NewRandom()

	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	// Log sending gRPC
	event := "Sending message to " + PRODUCTCATALOGSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	resp, err := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		ListProducts(newCtx, &pb.Empty{})

	// Check gRPC reply
	checkResponse(status.Code(err), PRODUCTCATALOGSERVICE, RequestID.String(), err)

	return resp.GetProducts(), err
}

func (fe *frontendServer) getProduct(ctx context.Context, id string) (*pb.Product, error) {
	RequestID, err := uuid.NewRandom()

	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	// Log sending gRPC
	event := "Sending message to " + PRODUCTCATALOGSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	resp, err := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		GetProduct(newCtx, &pb.GetProductRequest{Id: id})

	// Check gRPC reply
	checkResponse(status.Code(err), PRODUCTCATALOGSERVICE, RequestID.String(), err)

	return resp, err
}

func (fe *frontendServer) getCart(ctx context.Context, userID string) ([]*pb.CartItem, error) {
	RequestID, err := uuid.NewRandom()

	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	// Log sending gRPC
	event := "Sending message to " + CARTSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	resp, err := pb.NewCartServiceClient(fe.cartSvcConn).GetCart(newCtx, &pb.GetCartRequest{UserId: userID})

	// Check gRPC reply
	checkResponse(status.Code(err), CARTSERVICE, RequestID.String(), err)

	return resp.GetItems(), err
}

func (fe *frontendServer) emptyCart(ctx context.Context, userID string) error {
	RequestID, err := uuid.NewRandom()

	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	// Log sending gRPC
	event := "Sending message to " + CARTSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	_, err = pb.NewCartServiceClient(fe.cartSvcConn).EmptyCart(newCtx, &pb.EmptyCartRequest{UserId: userID})

	// Check gRPC reply
	checkResponse(status.Code(err), CARTSERVICE, RequestID.String(), err)

	return err
}

func (fe *frontendServer) insertCart(ctx context.Context, userID, productID string, quantity int32) error {
	RequestID, err := uuid.NewRandom()

	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	// Log sending gRPC
	event := "Sending message to " + CARTSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	_, err = pb.NewCartServiceClient(fe.cartSvcConn).AddItem(newCtx, &pb.AddItemRequest{
		UserId: userID,
		Item: &pb.CartItem{
			ProductId: productID,
			Quantity:  quantity},
	})

	// Check gRPC reply
	checkResponse(status.Code(err), CARTSERVICE, RequestID.String(), err)

	return err
}

func (fe *frontendServer) convertCurrency(ctx context.Context, money *pb.Money, currency string) (*pb.Money, error) {
	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	if avoidNoopCurrencyConversionRPC && money.GetCurrencyCode() == currency {
		return money, nil
	}

	// Log sending gRPC
	event := "Sending message to " + CURRENCYSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	res, err := pb.NewCurrencyServiceClient(fe.currencySvcConn).Convert(newCtx, &pb.CurrencyConversionRequest{
		From:   money,
		ToCode: currency})

	// Check gRPC reply
	checkResponse(status.Code(err), CURRENCYSERVICE, RequestID.String(), err)

	return res, nil
}

func (fe *frontendServer) getShippingQuote(ctx context.Context, items []*pb.CartItem, currency string) (*pb.Money, error) {
	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	// Log sending gRPC
	event := "Sending message to " + SHIPPINGSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	quote, err := pb.NewShippingServiceClient(fe.shippingSvcConn).GetQuote(newCtx,
		&pb.GetQuoteRequest{
			Address: nil,
			Items:   items})

	// Check gRPC reply
	checkResponse(status.Code(err), SHIPPINGSERVICE, RequestID.String(), err)

	localized, err := fe.convertCurrency(ctx, quote.GetCostUsd(), currency)

	if err != nil {
		emitLog("failed to convert currency for shipping cost", "ERROR")
	}

	return localized, errors.Wrap(err, "failed to convert currency for shipping cost")
}

func (fe *frontendServer) getRecommendations(ctx context.Context, userID string, productIDs []string) ([]*pb.Product, error) {
	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	// Log sending gRPC
	event := "Sending message to " + RECOMMENDATIONSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	resp, err := pb.NewRecommendationServiceClient(fe.recommendationSvcConn).ListRecommendations(newCtx,
		&pb.ListRecommendationsRequest{UserId: userID, ProductIds: productIDs})

	// Check gRPC reply
	checkResponse(status.Code(err), RECOMMENDATIONSERVICE, RequestID.String(), err)

	out := make([]*pb.Product, len(resp.GetProductIds()))

	for i, v := range resp.GetProductIds() {
		p, err := fe.getProduct(ctx, v)
		if err != nil {
			emitLog("failed to get recommended product info (#"+v+")", "ERROR")
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
	RequestID, err := uuid.NewRandom()
	if err != nil {
		emitLog(FRONTEND+": An error occurred while generating the RequestID", "ERROR")
	}

	// Add metadata to gRPC
	header := metadata.Pairs("requestid", RequestID.String(), "servicename", FRONTEND)
	metadataCtx := metadata.NewOutgoingContext(ctx, header)

	// Add gRPC timeout
	newCtx, cancel := context.WithTimeout(metadataCtx, time.Second)
	defer cancel()

	// Log sending gRPC
	event := "Sending message to " + ADSERVICE + " (request_id: " + RequestID.String() + ")"
	emitLog(event, "INFO")

	resp, err := pb.NewAdServiceClient(fe.adSvcConn).GetAds(newCtx, &pb.AdRequest{
		ContextKeys: ctxKeys,
	})

	// Check gRPC reply
	checkResponse(status.Code(err), ADSERVICE, RequestID.String(), err)

	return resp.GetAds(), errors.Wrap(err, "failed to get ads")
}
