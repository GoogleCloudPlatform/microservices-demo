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
	thrift "productcatalogservice/thriftgo/demo"
	"strings"
)

const (
	thriftHttpPath = "/ProductCatalogService"
)

type Handler struct{}

func convertProductType(item Product) *thrift.Product {
	p := thrift.Product{
		ID:          item.Id,
		Name:        item.Name,
		Description: item.Description,
		Picture:     item.Picture,
		Categories:  item.Categories,
		PriceUsd:    (*thrift.Money)(&item.PriceUsd),
	}
	return &p
}

func (h Handler) ListProducts(ctx context.Context) (result []*thrift.Product, err error) {
	log.Debugf("received a thrift rpc call to list productcatalog")
	fmt.Println("received a thrift rpc call to list productcatalog")
	for _, item := range products {
		result = append(result, convertProductType(item))
	}
	return
}

func (h Handler) GetProduct(ctx context.Context, product_id string) (result *thrift.Product, err error) {
	for _, item := range products {
		if product_id == item.Id {
			log.Debugf("received a thrift rpc call to get product for id[%s]", product_id)
			log.Println("received a thrift rpc call to get product for id[%s]", product_id)
			return convertProductType(item), nil
		}
	}
	return
}

func (h Handler) SearchProducts(ctx context.Context, query string) (result []*thrift.Product, err error) {
	log.Debug("received a thrift rpc call to search products")
	log.Println("received a thrift rpc call to search products")
	for _, product := range products {
		if strings.Contains(strings.ToLower(product.Name), strings.ToLower(query)) ||
			strings.Contains(strings.ToLower(product.Description), strings.ToLower(query)) {
			result = append(result, convertProductType(product))
		}
	}
	if len(result) > 0 {
		return
	}
	log.Info("Search product returned no result")
	return nil, fmt.Errorf("no products found matching %s", query)
}

func startThrift(port string) {
	processor := thrift.NewProductCatalogServiceProcessor(&Handler{})
	go func() {
		opt := NewDefaultOption()
		opt.HttpUrl = thriftHttpPath
		NewHttpThriftServer(fmt.Sprintf("0.0.0.0:%s", port), opt, processor)
		log.Info("Trift server terminated")
	}()
}
