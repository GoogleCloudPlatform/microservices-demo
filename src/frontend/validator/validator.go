// Copyright 2024 Google LLC
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
	"errors"
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

type Payload interface {
	Validate() error
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

// Implementations of the 'Payload' interface.
func (ad *AddToCartPayload) Validate() error {
	return validate.Struct(ad)
}

func (po *PlaceOrderPayload) Validate() error {
	return validate.Struct(po)
}

func (sc *SetCurrencyPayload) Validate() error {
	return validate.Struct(sc)
}

// Reusable error response function.
func ValidationErrorResponse(err error) error {
	validationErrs, ok := err.(validator.ValidationErrors)
	if !ok {
		return errors.New("invalid validation error format")
	}
	var msg string
	for _, err := range validationErrs {
		msg += fmt.Sprintf("Field '%s' is invalid: %s\n", err.Field(), err.Tag())
	}
	return fmt.Errorf(msg)
}
