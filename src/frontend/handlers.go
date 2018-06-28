package main

import (
	"context"
	"fmt"
	"frontend/money"
	"html/template"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/mux"

	pb "frontend/genproto"
)

var (
	templates = template.Must(template.New("").
		Funcs(template.FuncMap{
			"renderMoney": renderMoney,
		}).ParseGlob("templates/*.html"))
)

func ensureSessionID(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var sessionID string
		c, err := r.Cookie(cookieSessionID)
		if err == http.ErrNoCookie {
			u, _ := uuid.NewRandom()
			sessionID = u.String()
			http.SetCookie(w, &http.Cookie{
				Name:   cookieSessionID,
				Value:  sessionID,
				MaxAge: cookieMaxAge,
			})
		} else if err != nil {
			renderHTTPError(w, fmt.Errorf("unrecognized cookie error: %+v", err), http.StatusInternalServerError)
			return
		} else {
			sessionID = c.Value
		}
		ctx := context.WithValue(r.Context(), ctxKeySessionID{}, sessionID)
		r = r.WithContext(ctx)
		next(w, r)
	}
}

func (fe *frontendServer) homeHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[home] session_id=%s currency=%s", sessionID(r), currentCurrency(r))
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(w, fmt.Errorf("could not retrieve currencies: %+v", err), http.StatusInternalServerError)
		return
	}
	products, err := fe.getProducts(r.Context())
	if err != nil {
		renderHTTPError(w, fmt.Errorf("could not retrieve products: %+v", err), http.StatusInternalServerError)
		return
	}
	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		renderHTTPError(w, fmt.Errorf("could not retrieve cart: %+v", err), http.StatusInternalServerError)
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
			renderHTTPError(w, err, http.StatusInternalServerError)
			return
		}
		ps[i] = productView{p, price}
	}

	if err := templates.ExecuteTemplate(w, "home", map[string]interface{}{
		"user_currency": currentCurrency(r),
		"currencies":    currencies,
		"products":      ps,
		"session_id":    sessionID(r),
		"cart_size":     len(cart),
	}); err != nil {
		log.Println(err)
	}
}

func (fe *frontendServer) productHandler(w http.ResponseWriter, r *http.Request) {
	id := mux.Vars(r)["id"]
	if id == "" {
		renderHTTPError(w, fmt.Errorf("product id not specified"), http.StatusBadRequest)
		return
	}
	log.Printf("[productHandler] id=%s currency=%s session=%s", id, currentCurrency(r), sessionID(r))
	p, err := fe.getProduct(r.Context(), id)
	if err != nil {
		renderHTTPError(w, fmt.Errorf("could not retrieve product: %+v", err), http.StatusInternalServerError)
		return
	}
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(w, fmt.Errorf("could not retrieve currencies: %+v", err), http.StatusInternalServerError)
		return
	}

	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		renderHTTPError(w, fmt.Errorf("could not retrieve cart: %+v", err), http.StatusInternalServerError)
		return
	}

	price, err := fe.convertCurrency(r.Context(), p.GetPriceUsd(), currentCurrency(r))
	if err != nil {
		renderHTTPError(w, fmt.Errorf("failed to convert currency: %+v", err), http.StatusInternalServerError)
		return
	}

	recommendations, err := fe.getRecommendations(r.Context(), sessionID(r), []string{id})
	if err != nil {
		renderHTTPError(w, fmt.Errorf("failed to get product recommendations: %+v", err), http.StatusInternalServerError)
		return
	}

	product := struct {
		Item  *pb.Product
		Price *pb.Money
	}{p, price}

	if err := templates.ExecuteTemplate(w, "product", map[string]interface{}{
		"user_currency":   currentCurrency(r),
		"currencies":      currencies,
		"product":         product,
		"session_id":      sessionID(r),
		"recommendations": recommendations,
		"cart_size":       len(cart),
	}); err != nil {
		log.Println(err)
	}
}

func (fe *frontendServer) addToCartHandler(w http.ResponseWriter, r *http.Request) {
	quantity, _ := strconv.ParseUint(r.FormValue("quantity"), 10, 32)
	productID := r.FormValue("product_id")
	if productID == "" || quantity == 0 {
		renderHTTPError(w, fmt.Errorf("invalid form input"), http.StatusBadRequest)
		return
	}
	log.Printf("[addToCart] product_id=%s qty=%d session_id=%s", productID, quantity, sessionID(r))

	p, err := fe.getProduct(r.Context(), productID)
	if err != nil {
		renderHTTPError(w, fmt.Errorf("could not retrieve product: %+v", err), http.StatusInternalServerError)
		return
	}

	if err := fe.insertCart(r.Context(), sessionID(r), p.GetId(), int32(quantity)); err != nil {
		renderHTTPError(w, fmt.Errorf("failed to add to cart: %+v", err), http.StatusInternalServerError)
		return
	}
	w.Header().Set("location", "/cart")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) emptyCartHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[emptyCart] session_id=%s", sessionID(r))

	if err := fe.emptyCart(r.Context(), sessionID(r)); err != nil {
		renderHTTPError(w, fmt.Errorf("failed to empty cart: %+v", err), http.StatusInternalServerError)
		return
	}
	w.Header().Set("location", "/")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) viewCartHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[viewCart] session_id=%s", sessionID(r))
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(w, fmt.Errorf("could not retrieve currencies: %+v", err), http.StatusInternalServerError)
		return
	}
	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		renderHTTPError(w, fmt.Errorf("could not retrieve cart: %+v", err), http.StatusInternalServerError)
		return
	}

	recommendations, err := fe.getRecommendations(r.Context(), sessionID(r), cartIDs(cart))
	if err != nil {
		renderHTTPError(w, fmt.Errorf("failed to get product recommendations: %+v", err), http.StatusInternalServerError)
		return
	}

	shippingCost, err := fe.getShippingQuote(r.Context(), cart, currentCurrency(r))
	if err != nil {
		renderHTTPError(w, fmt.Errorf("failed to get shipping quote: %+v", err), http.StatusInternalServerError)
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
			renderHTTPError(w, fmt.Errorf("could not retrieve product #%s: %+v", item.GetProductId(), err), http.StatusInternalServerError)
			return
		}
		price, err := fe.convertCurrency(r.Context(), p.GetPriceUsd(), currentCurrency(r))
		if err != nil {
			renderHTTPError(w, fmt.Errorf("could not convert currency for product #%s: %+v", item.GetProductId(), err), http.StatusInternalServerError)
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
	if err := templates.ExecuteTemplate(w, "cart", map[string]interface{}{
		"user_currency":    currentCurrency(r),
		"currencies":       currencies,
		"session_id":       sessionID(r),
		"recommendations":  recommendations,
		"cart_size":        len(cart),
		"shipping_cost":    shippingCost,
		"total_cost":       totalPrice,
		"items":            items,
		"expiration_years": []int{year, year + 1, year + 2, year + 3, year + 4},
	}); err != nil {
		log.Println(err)
	}
}

func (fe *frontendServer) placeOrderHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[checkout] session_id=%s", sessionID(r))

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
		renderHTTPError(w, fmt.Errorf("failed to complete the order: %+v", err), http.StatusInternalServerError)
		return
	}
	log.Printf("order #%s completed", order.GetOrder().GetOrderId())

	order.GetOrder().GetItems()
	recommendations, _ := fe.getRecommendations(r.Context(), sessionID(r), nil)

	totalPaid := *order.GetOrder().GetShippingCost()
	for _, v := range order.GetOrder().GetItems() {
		totalPaid = money.Must(money.Sum(totalPaid, *v.GetCost()))
	}

	if err := templates.ExecuteTemplate(w, "order", map[string]interface{}{
		"session_id":      sessionID(r),
		"user_currency":   currentCurrency(r),
		"order":           order.GetOrder(),
		"total_paid":      &totalPaid,
		"recommendations": recommendations,
	}); err != nil {
		log.Println(err)
	}

	if err := fe.emptyCart(r.Context(), sessionID(r)); err != nil {
		log.Printf("WARN: failed to empty user (%s) cart after checkout: %+v", sessionID(r), err)
	}
}

func (fe *frontendServer) prepareCheckoutHandler(w http.ResponseWriter, r *http.Request) {
	streetAddress := r.FormValue("street_address")
	city := r.FormValue("city")
	state := r.FormValue("state")
	country := r.FormValue("country")
	zipCode, _ := strconv.ParseInt(r.FormValue("country"), 10, 32)

	log.Printf("[prepareCheckout] session_id=%+v", sessionID(r))
	_, _ = pb.NewCheckoutServiceClient(fe.checkoutSvcConn).CreateOrder(r.Context(),
		&pb.CreateOrderRequest{
			UserId:       sessionID(r),
			UserCurrency: currentCurrency(r),
			Address: &pb.Address{
				StreetAddress: streetAddress,
				City:          city,
				State:         state,
				ZipCode:       int32(zipCode),
				Country:       country,
			},
		})
}

func (fe *frontendServer) logoutHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[logout] session_id=%s", sessionID(r))
	for _, c := range r.Cookies() {
		c.Expires = time.Now().Add(-time.Hour * 24 * 365)
		c.MaxAge = -1
		http.SetCookie(w, c)
	}
	w.Header().Set("Location", "/")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) setCurrencyHandler(w http.ResponseWriter, r *http.Request) {
	cur := r.FormValue("currency_code")
	log.Printf("[setCurrency] session_id=%s code=%s", sessionID(r), cur)
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

func renderHTTPError(w http.ResponseWriter, err error, code int) {
	log.Printf("[error] %+v (code=%d)", err, code)
	w.WriteHeader(code)
	templates.ExecuteTemplate(w, "error", map[string]interface{}{
		"error":       err.Error(),
		"status_code": code,
		"status":      http.StatusText(code)})
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

func renderMoney(money pb.Money) string {
	return fmt.Sprintf("%s %d.%02d", money.GetCurrencyCode(), money.GetUnits(), money.GetNanos()/10000000)
}
