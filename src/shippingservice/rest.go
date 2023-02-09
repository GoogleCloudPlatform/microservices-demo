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
	"encoding/json"
	"fmt"
	"os"
	pb "shippingservice/genproto"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

func init() {
	log = logrus.New()
	log.Level = logrus.DebugLevel
	log.Out = os.Stdout
}

func startRest() {
	go func() {
		port := "60000"
		if os.Getenv("REST_PORT") != "" {
			port = os.Getenv("REST_PORT")
		}
		log.Infof("Rest server started on port %s", port)
		router := gin.Default()
		router.PUT("/get-quote", get_quote)
		router.PUT("/ship-order", ship_order)
		router.Run(fmt.Sprintf("0.0.0.0:%s", port))
	}()
}

func get_quote(c *gin.Context) {
	// Same logic as in grpc
	log.Info("[GetQuote] received rest request")
	defer log.Info("[GetQuote] completed rest request")

	// fix for unmarchalling tag zip_code -> zipCode
	in, err := c.GetRawData()
	if err != nil {
		c.JSON(501, gin.H{"error": "failed to read data"})
	}
	data := strings.ReplaceAll(string(in), "zip_code", "zipCode")
	order := &pb.GetQuoteRequest{}
	if err := json.Unmarshal([]byte(data), order); err != nil {
		c.JSON(501, gin.H{"error": "failed to parse GetQuoteRequest:"})
		return
	}

	count := len(order.Items)
	_ = count
	// TODO Base shipping quote on number of items

	// 1. Generate a quote based on the total number of items to be shipped.
	quote := CreateQuoteFromCount(0)

	// 2. Generate a response.
	c.JSON(200, pb.GetQuoteResponse{
		CostUsd: &pb.Money{
			CurrencyCode: "USD",
			Units:        int64(quote.Dollars),
			Nanos:        int32(quote.Cents * 10000000)},
	})
}

func ship_order(c *gin.Context) {
	// Same logic as in grpc
	log.Info("[ShipOrder] received request")
	defer log.Info("[ShipOrder] completed request")

	// fix for unmarchalling tag zip_code -> zipCode
	in, err := c.GetRawData()
	if err != nil {
		c.JSON(501, gin.H{"error": "failed to read data"})
	}
	data := strings.ReplaceAll(string(in), "zip_code", "zipCode")
	info := &pb.ShipOrderRequest{}
	if err := json.Unmarshal([]byte(data), info); err != nil {
		c.JSON(501, gin.H{"error": "failed to parse ShipOrderRequest"})
		return
	}

	// 1. Create a Tracking ID
	baseAddress := fmt.Sprintf("%s, %s, %s", info.Address.StreetAddress, info.Address.City, info.Address.State)
	id := CreateTrackingId(baseAddress)

	c.JSON(200, pb.ShipOrderResponse{
		TrackingId: id,
	})
}
