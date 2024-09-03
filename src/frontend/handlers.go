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
	"fmt"
	"html/template"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/gorilla/mux"
	"github.com/opentracing/opentracing-go"
	"github.com/pkg/errors"
	"github.com/signalfx/signalfx-go-tracing/ddtrace/tracer"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "github.com/signalfx/microservices-demo/src/frontend/genproto"
	"github.com/signalfx/microservices-demo/src/frontend/money"
)

type platformDetails struct {
	css      string
	provider string
}

var (
	templates = template.Must(template.New("").
			Funcs(template.FuncMap{
			"renderMoney": renderMoney,
		}).ParseGlob("templates/*.html"))
	plat platformDetails
)

func (fe *frontendServer) homeHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
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

	//get env and render correct platform banner.
	var env = os.Getenv("ENV_PLATFORM")
	plat = platformDetails{}
	plat.setPlatformDetails(strings.ToLower(env))

	if err := templates.ExecuteTemplate(w, "home", map[string]interface{}{
		"session_id":      sessionID(r),
		"request_id":      r.Context().Value(ctxKeyRequestID{}),
		"user_currency":   currentCurrency(r),
		"currencies":      currencies,
		"products":        ps,
		"cart_size":       cartSize(cart),
		"banner_color":    os.Getenv("BANNER_COLOR"), // illustrates canary deployments
		"ad":              fe.chooseAd(r.Context(), []string{}, log),
		"platform_css":    plat.css,
		"platform_name":   plat.provider,
		"rum_realm":       os.Getenv("RUM_REALM"),
		"rum_auth":        os.Getenv("RUM_AUTH"),
		"rum_app_name":    os.Getenv("RUM_APP_NAME"),
		"rum_environment": os.Getenv("RUM_ENVIRONMENT"),
		"rum_debug":       os.Getenv("RUM_DEBUG"),
	}); err != nil {
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
	} else {
		plat.provider = "Google Cloud"
		plat.css = "gcp-platform"
	}
}

func (fe *frontendServer) productHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
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
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to get product recommendations"), http.StatusInternalServerError)
		return
	}

	product := struct {
		Item  *pb.Product
		Price *pb.Money
	}{p, price}

	if err := templates.ExecuteTemplate(w, "product", map[string]interface{}{
		"session_id":      sessionID(r),
		"request_id":      r.Context().Value(ctxKeyRequestID{}),
		"ad":              fe.chooseAd(r.Context(), p.Categories, log),
		"user_currency":   currentCurrency(r),
		"currencies":      currencies,
		"product":         product,
		"recommendations": recommendations,
		"cart_size":       cartSize(cart),
		"platform_css":    plat.css,
		"platform_name":   plat.provider,
		"rum_realm":       os.Getenv("RUM_REALM"),
		"rum_auth":        os.Getenv("RUM_AUTH"),
		"rum_app_name":    os.Getenv("RUM_APP_NAME"),
		"rum_environment": os.Getenv("RUM_ENVIRONMENT"),
		"rum_debug":       os.Getenv("RUM_DEBUG"),
	}); err != nil {
		log.Println(err)
	}
}

func (fe *frontendServer) addToCartHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
	quantity, _ := strconv.ParseUint(r.FormValue("quantity"), 10, 32)
	productID := r.FormValue("product_id")
	if productID == "" || quantity == 0 {
		renderHTTPError(log, r, w, errors.New("invalid form input"), http.StatusBadRequest)
		return
	}
	log.WithField("product", productID).WithField("quantity", quantity).Debug("adding to cart")

	p, err := fe.getProduct(r.Context(), productID)
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve product"), http.StatusInternalServerError)
		return
	}

	if err := fe.insertCart(r.Context(), sessionID(r), p.GetId(), int32(quantity)); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to add to cart"), http.StatusInternalServerError)
		return
	}
	w.Header().Set("location", "/cart")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) emptyCartHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
	log.Debug("emptying cart")

	if err := fe.emptyCart(r.Context(), sessionID(r)); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to empty cart"), http.StatusInternalServerError)
		return
	}
	w.Header().Set("location", "/")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) viewCartHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
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
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to get product recommendations"), http.StatusInternalServerError)
		return
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

	log.Infof("🌈 ITEMS: %v", items)

	year := time.Now().Year()
	if err := templates.ExecuteTemplate(w, "cart", map[string]interface{}{
		"session_id":       sessionID(r),
		"request_id":       r.Context().Value(ctxKeyRequestID{}),
		"user_currency":    currentCurrency(r),
		"currencies":       currencies,
		"recommendations":  recommendations,
		"cart_size":        cartSize(cart),
		"shipping_cost":    shippingCost,
		"total_cost":       totalPrice,
		"items":            items,
		"expiration_years": []int{year, year + 1, year + 2, year + 3, year + 4},
		"platform_css":     plat.css,
		"platform_name":    plat.provider,
		"rum_realm":        os.Getenv("RUM_REALM"),
		"rum_auth":         os.Getenv("RUM_AUTH"),
		"rum_app_name":     os.Getenv("RUM_APP_NAME"),
		"rum_environment":  os.Getenv("RUM_ENVIRONMENT"),
		"rum_debug":        os.Getenv("RUM_DEBUG"),
	}); err != nil {
		log.Println(err)
	}
}

// generatePaymentHandler is for generating 500 error
func (fe *frontendServer) generatePaymentHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
	log.Debug("generate payment")

	// Fetch request data
	quantity, _ := strconv.ParseInt(r.FormValue("quantity"), 10, 32)
	productID := r.FormValue("product_id")

	// Validate request data
	if productID == "" || quantity <= 0 {
		renderHTTPError(log, r, w, errors.New("invalid form input"), http.StatusBadRequest)
		return
	}

	// GRPC client API call of checkoutService with request data
	_, err := pb.NewCheckoutServiceClient(fe.checkoutSvcConn).
		GeneratePayment(r.Context(), &pb.GeneratePaymentRequest{
			ProductId: productID,
			Quantity:  int32(quantity),
		})

	// Handle error
	// Return error with 500 status code.
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "Something went wrong with this request!"), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// generateSalesTaxHandler is for generating 408 error if country is 'france'
func (fe *frontendServer) generateSalesTaxHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())

	ctx := r.Context()
	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()

	// Fetch query parameterlog.Debug("generate Sales Tax")
	country := r.URL.Query().Get("country")

	// GRPC client API call of checkoutService
	// API request  is formed with fetched data
	_, err := pb.NewCheckoutServiceClient(fe.checkoutSvcConn).
		GenerateSalesTax(ctx, &pb.GenerateSalesTaxRequest{
			Country: country,
		})

	// Handle error
	// Return error with 408 status code.
	if err != nil {
		timeOutErr, ok := status.FromError(err)
		if ok {
			if timeOutErr.Code() == codes.DeadlineExceeded {
				renderHTTPError(log, r, w, errors.Wrap(err, "Something went wrong with this request!"), http.StatusRequestTimeout)
				return
			}
		}
		renderHTTPError(log, r, w, errors.Wrap(err, "Something went wrong with this request!"), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// generateCartEmptyHandler is for slow response of provided delay, default response time is 5 seconds
func (fe *frontendServer) generateCartEmptyHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
	log.Debug("generate Cart Empty")

	// Fetch query parameter
	u64, _ := strconv.ParseUint(r.URL.Query().Get("delay"), 10, 32)

	// GRPC client API call of checkoutService
	// API request  is formed with fetched data
	_, err := pb.NewCheckoutServiceClient(fe.checkoutSvcConn).
		GenerateCartEmpty(r.Context(), &pb.GenerateCartEmptyRequest{
			Delay: uint32(u64),
		})

	// Handle error
	// Return error with 500 status code.
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "Something went wrong with this request!"), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
}

func (fe *frontendServer) placeOrderHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
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
	)

	order, err := pb.NewCheckoutServiceClient(fe.checkoutSvcConn).
		PlaceOrder(r.Context(), &pb.PlaceOrderRequest{
			Email: email,
			CreditCard: &pb.CreditCardInfo{
				CreditCardNumber:          ccNumber,
				CreditCardExpirationMonth: int32(ccMonth),
				CreditCardExpirationYear:  int32(ccYear),
				CreditCardCvv:             int32(ccCVV)},
			UserId:       sessionID(r),
			UserCurrency: currentCurrency(r),
			Address: &pb.Address{
				StreetAddress: streetAddress,
				City:          city,
				State:         state,
				ZipCode:       int32(zipCode),
				Country:       country},
		})
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to complete the order"), http.StatusInternalServerError)
		return
	}
	log.WithField("order", order.GetOrder().GetOrderId()).Info("order placed")

	order.GetOrder().GetItems()
	recommendations, _ := fe.getRecommendations(r.Context(), sessionID(r), nil)

	totalPaid := *order.GetOrder().GetShippingCost()
	for _, v := range order.GetOrder().GetItems() {
		totalPaid = money.Must(money.Sum(totalPaid, *v.GetCost()))
	}

	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve currencies"), http.StatusInternalServerError)
		return
	}

	if err := templates.ExecuteTemplate(w, "order", map[string]interface{}{
		"session_id":      sessionID(r),
		"request_id":      r.Context().Value(ctxKeyRequestID{}),
		"user_currency":   currentCurrency(r),
		"currencies":      currencies,
		"order":           order.GetOrder(),
		"total_paid":      &totalPaid,
		"recommendations": recommendations,
		"platform_css":    plat.css,
		"platform_name":   plat.provider,
		"rum_realm":       os.Getenv("RUM_REALM"),
		"rum_auth":        os.Getenv("RUM_AUTH"),
		"rum_app_name":    os.Getenv("RUM_APP_NAME"),
		"rum_environment": os.Getenv("RUM_ENVIRONMENT"),
		"rum_debug":       os.Getenv("RUM_DEBUG"),
	}); err != nil {
		log.Println(err)
	}
}

func (fe *frontendServer) logoutHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
	log.Debug("logging out")
	for _, c := range r.Cookies() {
		c.Expires = time.Now().Add(-time.Hour * 24 * 365)
		c.MaxAge = -1
		http.SetCookie(w, c)
	}
	w.Header().Set("Location", "/")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) setCurrencyHandler(w http.ResponseWriter, r *http.Request) {
	log := getLoggerWithTraceFields(r.Context())
	cur := r.FormValue("currency_code")
	log.WithField("curr.new", cur).WithField("curr.old", currentCurrency(r)).
		Debug("setting currency")

	if cur != "" {
		http.SetCookie(w, &http.Cookie{
			Name:   cookieCurrency,
			Value:  cur,
			MaxAge: cookieMaxAge,
		})
	}
	referer := r.Header.Get("referer")
	if referer == "" {
		referer = "/"
	}
	w.Header().Set("Location", referer)
	w.WriteHeader(http.StatusFound)
}

// chooseAd queries for advertisements available and randomly chooses one, if
// available. It ignores the error retrieving the ad since it is not critical.
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
	templates.ExecuteTemplate(w, "error", map[string]interface{}{
		"session_id":      sessionID(r),
		"request_id":      r.Context().Value(ctxKeyRequestID{}),
		"error":           errMsg,
		"status_code":     code,
		"rum_realm":       os.Getenv("RUM_REALM"),
		"rum_auth":        os.Getenv("RUM_AUTH"),
		"rum_app_name":    os.Getenv("RUM_APP_NAME"),
		"rum_environment": os.Getenv("RUM_ENVIRONMENT"),
		"rum_debug":       os.Getenv("RUM_DEBUG"),
		"status":          http.StatusText(code)})
}

func currentCurrency(r *http.Request) string {
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

// get total # of items in cart
func cartSize(c []*pb.CartItem) int {
	cartSize := 0
	for _, item := range c {
		cartSize += int(item.GetQuantity())
	}
	return cartSize
}

func renderMoney(money pb.Money) string {
	return fmt.Sprintf("%s %d.%02d", money.GetCurrencyCode(), money.GetUnits(), money.GetNanos()/10000000)
}

func getLoggerWithTraceFields(ctx context.Context) *logrus.Entry {
	log := ctx.Value(ctxKeyLog{}).(logrus.FieldLogger)
	fields := logrus.Fields{}
	if span := opentracing.SpanFromContext(ctx); span != nil {
		spanCtx := span.Context()
		fields["trace_id"] = tracer.TraceIDHex(spanCtx)
		fields["span_id"] = tracer.SpanIDHex(spanCtx)
		fields["service.name"] = "frontend"
	}
	return log.WithFields(fields)
}
