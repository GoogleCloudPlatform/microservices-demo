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
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"math/rand"
	"net"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/gorilla/mux"
	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"
	"github.com/GoogleCloudPlatform/microservices-demo/src/frontend/money"
	"github.com/GoogleCloudPlatform/microservices-demo/src/frontend/validator"
)

type platformDetails struct {
	css      string
	provider string
}

var (
	frontendMessage  = strings.TrimSpace(os.Getenv("FRONTEND_MESSAGE"))
	isCymbalBrand    = "true" == strings.ToLower(os.Getenv("CYMBAL_BRANDING"))
	assistantEnabled = "true" == strings.ToLower(os.Getenv("ENABLE_ASSISTANT"))
	templates        = template.Must(template.New("").
				Funcs(template.FuncMap{
			"renderMoney":        renderMoney,
			"renderCurrencyLogo": renderCurrencyLogo,
		}).ParseGlob("templates/*.html"))
	plat platformDetails
)


type couponDef struct {
	DiscountUSD int64
	MinOrderUSD int64
}

var couponDefs = map[string]couponDef{
	"SAVE10":  {DiscountUSD: 10, MinOrderUSD: 50},
	"SAVE50":  {DiscountUSD: 50, MinOrderUSD: 200},
	"SAVE100": {DiscountUSD: 100, MinOrderUSD: 350},
}


var couponOrder = []string{"SAVE10", "SAVE50", "SAVE100"}

var validEnvs = []string{"local", "gcp", "azure", "aws", "onprem", "alibaba"}
// Home godoc
//
// @Summary      Home page
// @Description  Displays the Hipster Shop home page with the list of available products.
// @Tags         Home
// @Accept       json
// @Produce      text/html
//
// @Success      200 {string} string "Home page rendered successfully"
// @Failure      500 {string} string "Internal Server Error"
//
// @Router       / [get]
func (fe *frontendServer) homeHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	log.WithField("currency", currentCurrency(r)).Info("home")
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve currencies"), http.StatusInternalServerError)
		return
	}
	products, err := fe.getProducts(r.Context())
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve products"), http.StatusInternalServerError)
		return
	}
	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve cart"), http.StatusInternalServerError)
		return
	}

	type productView struct {
		Item  *pb.Product
		Price *pb.Money
	}
	ps := make([]productView, len(products))
	for i, p := range products {
		price, err := fe.convertCurrency(r.Context(), p.GetPriceUsd(), currentCurrency(r))
		if err != nil {
			renderHTTPError(log, r, w, errors.Wrapf(err, "failed to do currency conversion for product %s", p.GetId()), http.StatusInternalServerError)
			return
		}
		ps[i] = productView{p, price}
	}

	var env = os.Getenv("ENV_PLATFORM")
	if env == "" || stringinSlice(validEnvs, env) == false {
		fmt.Println("env platform is either empty or invalid")
		env = "local"
	}
	addrs, err := net.LookupHost("metadata.google.internal.")
	if err == nil && len(addrs) >= 0 {
		log.Debugf("Detected Google metadata server: %v, setting ENV_PLATFORM to GCP.", addrs)
		env = "gcp"
	}

	log.Debugf("ENV_PLATFORM is: %s", env)
	plat = platformDetails{}
	plat.setPlatformDetails(strings.ToLower(env))

	if err := templates.ExecuteTemplate(w, "home", injectCommonTemplateData(r, map[string]interface{}{
		"show_currency": true,
		"currencies":    currencies,
		"products":      ps,
		"cart_size":     cartSize(cart),
		"banner_color":  os.Getenv("BANNER_COLOR"),
		"ad":            fe.chooseAd(r.Context(), []string{}, log),
	})); err != nil {
		log.Error(err)
	}
}

func (plat *platformDetails) setPlatformDetails(env string) {
	if env == "aws" {
		plat.provider = "AWS"
		plat.css = "aws-platform"
	} else if env == "onprem" {
		plat.provider = "On-Premises"
		plat.css = "onprem-platform"
	} else if env == "azure" {
		plat.provider = "Azure"
		plat.css = "azure-platform"
	} else if env == "gcp" {
		plat.provider = "Google Cloud"
		plat.css = "gcp-platform"
	} else if env == "alibaba" {
		plat.provider = "Alibaba Cloud"
		plat.css = "alibaba-platform"
	} else {
		plat.provider = "local"
		plat.css = "local"
	}
}
// ProductDetails godoc
//
// @Summary      View product details
// @Description  Displays detailed information for a specific product.
// @Tags         Product
// @Accept       json
// @Produce      text/html
//
// @Param        id path string true "Product ID"
//
// @Success      200 {string} string "Product page rendered successfully"
// @Failure      404 {string} string "Product not found"
// @Failure      500 {string} string "Internal Server Error"
//
// @Router       /product/{id} [get]
func (fe *frontendServer) productHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	id := mux.Vars(r)["id"]
	if id == "" {
		renderHTTPError(log, r, w, errors.New("product id not specified"), http.StatusBadRequest)
		return
	}
	log.WithField("id", id).WithField("currency", currentCurrency(r)).
		Debug("serving product page")

	p, err := fe.getProduct(r.Context(), id)
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve product"), http.StatusInternalServerError)
		return
	}
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve currencies"), http.StatusInternalServerError)
		return
	}

	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve cart"), http.StatusInternalServerError)
		return
	}

	price, err := fe.convertCurrency(r.Context(), p.GetPriceUsd(), currentCurrency(r))
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to convert currency"), http.StatusInternalServerError)
		return
	}

	recommendations, err := fe.getRecommendations(r.Context(), sessionID(r), []string{id})
	if err != nil {
		log.WithField("error", err).Warn("failed to get product recommendations")
	}

	product := struct {
		Item  *pb.Product
		Price *pb.Money
	}{p, price}

	var packagingInfo *PackagingInfo = nil
	if isPackagingServiceConfigured() {
		packagingInfo, err = httpGetPackagingInfo(id)
		if err != nil {
			fmt.Println("Failed to obtain product's packaging info:", err)
		}
	}

	if err := templates.ExecuteTemplate(w, "product", injectCommonTemplateData(r, map[string]interface{}{
		"ad":              fe.chooseAd(r.Context(), p.Categories, log),
		"show_currency":   true,
		"currencies":      currencies,
		"product":         product,
		"recommendations": recommendations,
		"cart_size":       cartSize(cart),
		"packagingInfo":   packagingInfo,
	})); err != nil {
		log.Println(err)
	}
}
// AddToCart godoc
//
// @Summary Add product to cart
// @Description Adds a product to the current shopping cart.
// @Tags Cart
// @Accept application/x-www-form-urlencoded
// @Produce text/html
//
// @Param product_id formData string true "Product ID"
// @Param quantity formData integer true "Quantity"
//
// @Success 302 "Redirect to cart"
// @Failure 422 "Validation Error"
// @Failure 500 "Internal Server Error"
//
// @Router /cart [post]
func (fe *frontendServer) addToCartHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	quantity, _ := strconv.ParseUint(r.FormValue("quantity"), 10, 32)
	productID := r.FormValue("product_id")
	payload := validator.AddToCartPayload{
		Quantity:  quantity,
		ProductID: productID,
	}
	if err := payload.Validate(); err != nil {
		renderHTTPError(log, r, w, validator.ValidationErrorResponse(err), http.StatusUnprocessableEntity)
		return
	}
	log.WithField("product", payload.ProductID).WithField("quantity", payload.Quantity).Debug("adding to cart")

	p, err := fe.getProduct(r.Context(), payload.ProductID)
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve product"), http.StatusInternalServerError)
		return
	}

	if err := fe.insertCart(r.Context(), sessionID(r), p.GetId(), int32(payload.Quantity)); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to add to cart"), http.StatusInternalServerError)
		return
	}
	w.Header().Set("location", baseUrl+"/cart")
	w.WriteHeader(http.StatusFound)
}

// EmptyCart godoc
//
// @Summary      Empty shopping cart
// @Description  Removes all items from the current user's shopping cart.
// @Tags         Cart
// @Accept       json
// @Produce      text/html
//
// @Success      200 {string} string "Cart emptied successfully"
// @Failure      500 {string} string "Internal Server Error"
//
// @Router       /cart/empty [post]
func (fe *frontendServer) emptyCartHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	log.Debug("emptying cart")

	if err := fe.emptyCart(r.Context(), sessionID(r)); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to empty cart"), http.StatusInternalServerError)
		return
	}
	w.Header().Set("location", baseUrl+"/")
	w.WriteHeader(http.StatusFound)
}
// ViewCart godoc
//
//	@Summary		View shopping cart
//	@Description	Retrieves and displays the current user's shopping cart, including cart items, quantities, prices, and total amount.
//	@Tags			Cart
//	@Accept			json
//	@Produce		text/html
//
//	@Param			coupon_error	query	string	false	"Coupon validation error message, set when redirected here from /cart/checkout"
//	@Param			coupon_code		query	string	false	"Coupon code to pre-fill in the form, set when redirected here from /cart/checkout"
//
//	@Success		200	{string}	string	"Cart page rendered successfully"
//	@Failure		500	{string}	string	"Internal Server Error"
//
//	@Router			/cart [get]
func (fe *frontendServer) viewCartHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	log.Debug("view user cart")
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve currencies"), http.StatusInternalServerError)
		return
	}
	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve cart"), http.StatusInternalServerError)
		return
	}

	recommendations, err := fe.getRecommendations(r.Context(), sessionID(r), cartIDs(cart))
	if err != nil {
		log.WithField("error", err).Warn("failed to get product recommendations")
	}

	shippingCost, err := fe.getShippingQuote(r.Context(), cart, currentCurrency(r))
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to get shipping quote"), http.StatusInternalServerError)
		return
	}

	type cartItemView struct {
		Item     *pb.Product
		Quantity int32
		Price    *pb.Money
	}
	items := make([]cartItemView, len(cart))
	totalPrice := pb.Money{CurrencyCode: currentCurrency(r)}
	for i, item := range cart {
		p, err := fe.getProduct(r.Context(), item.GetProductId())
		if err != nil {
			renderHTTPError(log, r, w, errors.Wrapf(err, "could not retrieve product #%s", item.GetProductId()), http.StatusInternalServerError)
			return
		}
		price, err := fe.convertCurrency(r.Context(), p.GetPriceUsd(), currentCurrency(r))
		if err != nil {
			renderHTTPError(log, r, w, errors.Wrapf(err, "could not convert currency for product #%s", item.GetProductId()), http.StatusInternalServerError)
			return
		}

		multPrice := money.MultiplySlow(*price, uint32(item.GetQuantity()))
		items[i] = cartItemView{
			Item:     p,
			Quantity: item.GetQuantity(),
			Price:    &multPrice}
		totalPrice = money.Must(money.Sum(totalPrice, multPrice))
	}
	totalPrice = money.Must(money.Sum(totalPrice, *shippingCost))
	year := time.Now().Year()

	
	couponError := r.URL.Query().Get("coupon_error")
	
	lastCoupon := r.URL.Query().Get("coupon_code")

	
	type couponOptionView struct {
		Code        string
		DiscountUSD int64
		MinOrderUSD int64
	}
	couponOptions := make([]couponOptionView, 0, len(couponOrder))
	for _, code := range couponOrder {
		def := couponDefs[code]
		couponOptions = append(couponOptions, couponOptionView{Code: code, DiscountUSD: def.DiscountUSD, MinOrderUSD: def.MinOrderUSD})
	}

	if err := templates.ExecuteTemplate(w, "cart", injectCommonTemplateData(r, map[string]interface{}{
		"currencies":       currencies,
		"recommendations":  recommendations,
		"cart_size":        cartSize(cart),
		"shipping_cost":    shippingCost,
		"show_currency":    true,
		"total_cost":       totalPrice,
		"items":            items,
		"expiration_years": []int{year, year + 1, year + 2, year + 3, year + 4},
		"coupon_error":   couponError,
		"last_coupon":    lastCoupon,
		"coupon_options": couponOptions,
	})); err != nil {
		log.Println(err)
	}
}


// PlaceOrder godoc
//
// @Summary      Place an order
// @Description  Processes the checkout form, validates the input, places the order using the Checkout gRPC service, and renders the order confirmation page.
// @Tags         Checkout
// @Accept       application/x-www-form-urlencoded
// @Produce      text/html
//
// @Param email formData string true "Customer email"
// @Param street_address formData string true "Street address"
// @Param zip_code formData string true "ZIP/Postal code"
// @Param city formData string true "City"
// @Param state formData string true "State"
// @Param country formData string true "Country"
// @Param credit_card_number formData string true "Credit card number"
// @Param credit_card_expiration_month formData integer true "Credit card expiration month"
// @Param credit_card_expiration_year formData integer true "Credit card expiration year"
// @Param credit_card_cvv formData integer true "Credit card CVV"
// @Param coupon_code formData string false "Coupon code"
//
// @Success 200 {string} string "Order placed successfully"
// @Success 302 {string} string "Redirect to /cart with a coupon_error when the submitted coupon is unknown or below its minimum order amount"
// @Failure 422 {string} string "Validation Error"
// @Failure 500 {string} string "Internal server error"
//
// @Router /cart/checkout [post]
func (fe *frontendServer) placeOrderHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	log.Debug("placing order")

	var (
		email         = r.FormValue("email")
		streetAddress = r.FormValue("street_address")
		zipCode, _    = strconv.ParseInt(r.FormValue("zip_code"), 10, 32)
		city          = r.FormValue("city")
		state         = r.FormValue("state")
		country       = r.FormValue("country")
		ccNumber      = r.FormValue("credit_card_number")
		ccMonth, _    = strconv.ParseInt(r.FormValue("credit_card_expiration_month"), 10, 32)
		ccYear, _     = strconv.ParseInt(r.FormValue("credit_card_expiration_year"), 10, 32)
		ccCVV, _      = strconv.ParseInt(r.FormValue("credit_card_cvv"), 10, 32)
		couponCode    = strings.TrimSpace(strings.ToUpper(r.FormValue("coupon_code")))
	)

	
	if couponCode != "" {
		if _, ok := couponDefs[couponCode]; !ok {
			http.Redirect(w, r,
				baseUrl+"/cart?coupon_error=Invalid+coupon+code+%22"+couponCode+"%22.+Please+try+again.&coupon_code="+couponCode,
				http.StatusFound)
			return
		}
	}

	payload := validator.PlaceOrderPayload{
		Email:         email,
		StreetAddress: streetAddress,
		ZipCode:       zipCode,
		City:          city,
		State:         state,
		Country:       country,
		CcNumber:      ccNumber,
		CcMonth:       ccMonth,
		CcYear:        ccYear,
		CcCVV:         ccCVV,
	}
	if err := payload.Validate(); err != nil {
		renderHTTPError(log, r, w, validator.ValidationErrorResponse(err), http.StatusUnprocessableEntity)
		return
	}

	order, err := pb.NewCheckoutServiceClient(fe.checkoutSvcConn).
		PlaceOrder(r.Context(), &pb.PlaceOrderRequest{
			Email: payload.Email,
			CreditCard: &pb.CreditCardInfo{
				CreditCardNumber:          payload.CcNumber,
				CreditCardExpirationMonth: int32(payload.CcMonth),
				CreditCardExpirationYear:  int32(payload.CcYear),
				CreditCardCvv:             int32(payload.CcCVV)},
			UserId:       sessionID(r),
			UserCurrency: currentCurrency(r),
			Address: &pb.Address{
				StreetAddress: payload.StreetAddress,
				City:          payload.City,
				State:         payload.State,
				ZipCode:       int32(payload.ZipCode),
				Country:       payload.Country,
			},
			CouponCode: couponCode,
 		})
	if err != nil {
	
		if couponCode != "" {
			if st, ok := status.FromError(err); ok &&
				(st.Code() == codes.FailedPrecondition || st.Code() == codes.InvalidArgument) {
				http.Redirect(w, r,
					baseUrl+"/cart?coupon_error="+url.QueryEscape(st.Message())+"&coupon_code="+url.QueryEscape(couponCode),
					http.StatusFound)
				return
			}
		}
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to complete the order"), http.StatusInternalServerError)
		return
	}
	log.WithField("order", order.GetOrder().GetOrderId()).Info("order placed")

	order.GetOrder().GetItems()
	recommendations, _ := fe.getRecommendations(r.Context(), sessionID(r), nil)

	type orderItemView struct {
		Item     *pb.Product
		Quantity int32
		Price    *pb.Money
	}

	totalPaid := *order.GetOrder().GetShippingCost()
	orderItems := make([]orderItemView, len(order.GetOrder().GetItems()))
	for i, v := range order.GetOrder().GetItems() {
		multPrice := money.MultiplySlow(*v.GetCost(), uint32(v.GetItem().GetQuantity()))
		totalPaid = money.Must(money.Sum(totalPaid, multPrice))

		p, err := fe.getProduct(r.Context(), v.GetItem().GetProductId())
		if err != nil {
			renderHTTPError(log, r, w, errors.Wrapf(err, "could not retrieve product #%s", v.GetItem().GetProductId()), http.StatusInternalServerError)
			return
		}
		orderItems[i] = orderItemView{Item: p, Quantity: v.GetItem().GetQuantity(), Price: &multPrice}
	}

	discount := order.GetOrder().GetDiscountAmount()
	if discount != nil && discount.GetUnits() > 0 {
		negativeDiscount := pb.Money{
			CurrencyCode: discount.GetCurrencyCode(),
			Units:        -discount.GetUnits(),
			Nanos:        -discount.GetNanos(),
		}
		if newTotal, err := money.Sum(totalPaid, negativeDiscount); err == nil && newTotal.Units >= 0 {
			totalPaid = newTotal
		} else {
			// discount was larger than total — order was free
			totalPaid = pb.Money{CurrencyCode: discount.GetCurrencyCode(), Units: 0, Nanos: 0}
		}
	}

	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve currencies"), http.StatusInternalServerError)
		return
	}

	
	var discountAmount *pb.Money
	var couponCodeUsed string
	if couponCode != "" {
		discountAmount = order.GetOrder().GetDiscountAmount()
		couponCodeUsed = order.GetOrder().GetCouponCodeUsed()
	}

	if err := templates.ExecuteTemplate(w, "order", injectCommonTemplateData(r, map[string]interface{}{
		"show_currency":    false,
		"currencies":       currencies,
		"order":            order.GetOrder(),
		"order_items":      orderItems,
		"total_paid":       &totalPaid,
		"recommendations":  recommendations,
		"discount_amount":  discountAmount,
		"coupon_code_used": couponCodeUsed,
	})); err != nil {
		log.Println(err)
	}
}

// AssistantPage godoc
//
// @Summary      Display shopping assistant page
// @Description  Renders the shopping assistant interface for interacting with the AI assistant.
// @Tags         Assistant
// @Accept       json
// @Produce      text/html
//
// @Success      200 {string} string "Assistant page rendered successfully"
// @Failure      500 {string} string "Internal Server Error"
//
// @Router       /assistant [get]
func (fe *frontendServer) assistantHandler(w http.ResponseWriter, r *http.Request) {
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve currencies"), http.StatusInternalServerError)
		return
	}

	if err := templates.ExecuteTemplate(w, "assistant", injectCommonTemplateData(r, map[string]interface{}{
		"show_currency": false,
		"currencies":    currencies,
	})); err != nil {
		log.Println(err)
	}
}
// Logout godoc
//
// @Summary      Logout user
// @Description  Logs out the current user by clearing the session and redirects to the home page.
// @Tags         Authentication
// @Accept       json
// @Produce      text/html
//
// @Success      302 {string} string "Redirect to home page after logout"
// @Failure      500 {string} string "Internal Server Error"
//
// @Router       /logout [get]
func (fe *frontendServer) logoutHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	log.Debug("logging out")
	for _, c := range r.Cookies() {
		c.Expires = time.Now().Add(-time.Hour * 24 * 365)
		c.MaxAge = -1
		http.SetCookie(w, c)
	}
	w.Header().Set("Location", baseUrl+"/")
	w.WriteHeader(http.StatusFound)
}
// GetProductMetadata godoc
//
// @Summary      Get product metadata
// @Description  Returns product metadata for one or more product IDs.
// @Tags         Product
// @Accept       json
// @Produce      application/json
//
// @Param        ids path string true "Comma-separated product IDs"
//
// @Success      200 {object} map[string]interface{}
// @Failure      400 {string} string "Invalid product ID"
// @Failure      404 {string} string "Product not found"
//
// @Router       /product-meta/{ids} [get]
func (fe *frontendServer) getProductByID(w http.ResponseWriter, r *http.Request) {
	id := mux.Vars(r)["ids"]
	if id == "" {
		return
	}

	p, err := fe.getProduct(r.Context(), id)
	if err != nil {
		return
	}

	jsonData, err := json.Marshal(p)
	if err != nil {
		fmt.Println(err)
		return
	}

	w.Write(jsonData)
	w.WriteHeader(http.StatusOK)
}
// ChatBot godoc
//
// @Summary      Chat with shopping assistant
// @Description  Sends a user query to the shopping assistant and returns the generated response.
// @Tags         Assistant
// @Accept       application/json
// @Produce      application/json
//
// @Param        request body map[string]interface{} true "Chat request"
//
// @Success      200 {object} map[string]interface{}
// @Failure      400 {string} string "Invalid request"
// @Failure      500 {string} string "Internal Server Error"
//
// @Router       /bot [post]
func (fe *frontendServer) chatBotHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	type Response struct {
		Message string `json:"message"`
	}

	type LLMResponse struct {
		Content string         `json:"content"`
		Details map[string]any `json:"details"`
	}

	var response LLMResponse

	url := "http://" + fe.shoppingAssistantSvcAddr
	req, err := http.NewRequest(http.MethodPost, url, r.Body)
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to create request"), http.StatusInternalServerError)
		return
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to send request"), http.StatusInternalServerError)
		return
	}

	body, err := io.ReadAll(res.Body)
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to read response"), http.StatusInternalServerError)
		return
	}

	fmt.Printf("%+v\n", body)
	fmt.Printf("%+v\n", res)

	err = json.Unmarshal(body, &response)
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to unmarshal body"), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(Response{Message: response.Content})
	w.WriteHeader(http.StatusOK)
}
// SetCurrency godoc
//
// @Summary      Set preferred currency
// @Description  Updates the user's preferred currency and refreshes the current session.
// @Tags         Currency
// @Accept       application/x-www-form-urlencoded
// @Produce      text/html
//
// @Param        currency_code formData string true "Currency code (e.g. USD, EUR, INR)"
//
// @Success      302 {string} string "Redirect after updating currency"
// @Failure      400 {string} string "Invalid currency code"
// @Failure      500 {string} string "Internal Server Error"
//
// @Router       /setCurrency [post]
func (fe *frontendServer) setCurrencyHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)

	// When currency is locked via DEFAULT_CURRENCY env var, ignore the request.
	if lockedCurrency != "" {
		log.Debug("currency is locked via DEFAULT_CURRENCY env var; ignoring setCurrency request")
		referer := r.Header.Get("referer")
		if referer == "" {
			referer = baseUrl + "/"
		}
		w.Header().Set("Location", referer)
		w.WriteHeader(http.StatusFound)
		return
	}

	cur := r.FormValue("currency_code")
	payload := validator.SetCurrencyPayload{Currency: cur}
	if err := payload.Validate(); err != nil {
		renderHTTPError(log, r, w, validator.ValidationErrorResponse(err), http.StatusUnprocessableEntity)
		return
	}
	log.WithField("curr.new", payload.Currency).WithField("curr.old", currentCurrency(r)).
		Debug("setting currency")

	if payload.Currency != "" {
		http.SetCookie(w, &http.Cookie{
			Name:   cookieCurrency,
			Value:  payload.Currency,
			MaxAge: cookieMaxAge,
		})
	}
	referer := r.Header.Get("referer")
	if referer == "" {
		referer = baseUrl + "/"
	}
	w.Header().Set("Location", referer)
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) chooseAd(ctx context.Context, ctxKeys []string, log logrus.FieldLogger) *pb.Ad {
	ads, err := fe.getAd(ctx, ctxKeys)
	if err != nil {
		log.WithField("error", err).Warn("failed to retrieve ads")
		return nil
	}
	return ads[rand.Intn(len(ads))]
}

func renderHTTPError(log logrus.FieldLogger, r *http.Request, w http.ResponseWriter, err error, code int) {
	log.WithField("error", err).Error("request error")
	errMsg := fmt.Sprintf("%+v", err)

	w.WriteHeader(code)

	if templateErr := templates.ExecuteTemplate(w, "error", injectCommonTemplateData(r, map[string]interface{}{
		"error":       errMsg,
		"status_code": code,
		"status":      http.StatusText(code),
	})); templateErr != nil {
		log.Println(templateErr)
	}
}

func injectCommonTemplateData(r *http.Request, payload map[string]interface{}) map[string]interface{} {
	data := map[string]interface{}{
		"session_id":        sessionID(r),
		"request_id":        r.Context().Value(ctxKeyRequestID{}),
		"user_currency":     currentCurrency(r),
		"currency_locked":   lockedCurrency != "",
		"platform_css":      plat.css,
		"platform_name":     plat.provider,
		"is_cymbal_brand":   isCymbalBrand,
		"assistant_enabled": assistantEnabled,
		"deploymentDetails": deploymentDetailsMap,
		"frontendMessage":   frontendMessage,
		"currentYear":       time.Now().Year(),
		"baseUrl":           baseUrl,
	}

	for k, v := range payload {
		data[k] = v
	}

	return data
}

func currentCurrency(r *http.Request) string {
	if lockedCurrency != "" {
		return lockedCurrency
	}
	c, _ := r.Cookie(cookieCurrency)
	if c != nil {
		return c.Value
	}
	return defaultCurrency
}

func sessionID(r *http.Request) string {
	v := r.Context().Value(ctxKeySessionID{})
	if v != nil {
		return v.(string)
	}
	return ""
}

func cartIDs(c []*pb.CartItem) []string {
	out := make([]string, len(c))
	for i, v := range c {
		out[i] = v.GetProductId()
	}
	return out
}

func cartSize(c []*pb.CartItem) int {
	cartSize := 0
	for _, item := range c {
		cartSize += int(item.GetQuantity())
	}
	return cartSize
}

func renderMoney(money pb.Money) string {
	currencyLogo := renderCurrencyLogo(money.GetCurrencyCode())
	return fmt.Sprintf("%s%d.%02d", currencyLogo, money.GetUnits(), money.GetNanos()/10000000)
}

func renderCurrencyLogo(currencyCode string) string {
	logos := map[string]string{
		"USD": "$",
		"CAD": "$",
		"JPY": "¥",
		"EUR": "€",
		"TRY": "₺",
		"GBP": "£",
	}

	logo := "$"
	if val, ok := logos[currencyCode]; ok {
		logo = val
	}
	return logo
}

func stringinSlice(slice []string, val string) bool {
	for _, item := range slice {
		if item == val {
			return true
		}
	}
	return false
}