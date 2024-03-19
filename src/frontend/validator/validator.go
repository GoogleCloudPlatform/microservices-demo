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

package validator

import (
	"fmt"

	"github.com/go-playground/validator/v10"
)

var validate *validator.Validate

// init() is a special function that will run when this package is imported.
// It instantiates a SINGLE instance of *validator.Validate with the added
// benefit of caching struct info and validations.
func init() {
	validate = validator.New(validator.WithRequiredStructEnabled())
}

type AddToCartPayload struct {
	Quantity  uint64 `validate:"required,gte=1,lte=10"`
	ProductID string `validate:"required"`
}

type PlaceOrderPayload struct {
	Email         string `validate:"required,email"`
	StreetAddress string `validate:"required,max=512"`
	ZipCode       int64  `validate:"required"`
	City          string `validate:"required,max=128"`
	State         string `validate:"required,max=128"`
	Country       string `validate:"required,max=128"`
	CcNumber      string `validate:"required,credit_card"`
	CcMonth       int64  `validate:"required,gte=1,lte=12"`
	CcYear        int64  `validate:"required"`
	CcCVV         int64  `validate:"required"`
}

type SetCurrencyPayload struct {
	Currency string `validate:"required,iso4217"`
}

func (ad *AddToCartPayload) Validate() error {
	err := validate.Struct(ad)
	if err == nil {
		return nil
	}
	validationErr, ok := err.(validator.ValidationErrors)
	if !ok {
		return err
	}
	return errorResponse(validationErr)
}

func (po *PlaceOrderPayload) Validate() error {
	err := validate.Struct(po)
	if err == nil {
		return nil
	}
	validationErr, ok := err.(validator.ValidationErrors)
	if !ok {
		return err
	}
	return errorResponse(validationErr)
}

func (sc *SetCurrencyPayload) Validate() error {
	err := validate.Struct(sc)
	if err == nil {
		return nil
	}
	validationErr, ok := err.(validator.ValidationErrors)
	if !ok {
		return err
	}
	return errorResponse(validationErr)
}

func errorResponse(validationErr validator.ValidationErrors) error {
	var msg string
	for _, err := range validationErr {
		msg += fmt.Sprintf("the %s in your request is invalid.\n", err.Field())
	}
	return fmt.Errorf(msg)
}
