package main

import (
	"context"
	"fmt"
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
	templates = template.Must(template.ParseGlob("templates/*.html"))
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
			http.Error(w, fmt.Sprintf("unrecognized cookie error: %+v", err), http.StatusInternalServerError)
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
	log.Printf("[home] session_id=%+v currency=%s", sessionID(r), currentCurrency(r))
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve currencies: %+v", err), http.StatusInternalServerError)
		return
	}
	products, err := fe.getProducts(r.Context())
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve products: %+v", err), http.StatusInternalServerError)
		return
	}
	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve cart: %+v", err), http.StatusInternalServerError)
		return
	}

	type productView struct {
		Item  *pb.Product
		Price *pb.Money
	}
	ps := make([]productView, len(products))
	for i, p := range products {
		price, err := fe.convertCurrency(r.Context(), &pb.Money{
			Amount:       p.PriceUsd,
			CurrencyCode: defaultCurrency,
		}, currentCurrency(r))
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
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
		http.Error(w, "product id not specified", http.StatusBadRequest)
		return
	}
	log.Printf("[productHandler] id=%s currency=%s session=%s", id, currentCurrency(r), sessionID(r))
	p, err := fe.getProduct(r.Context(), id)
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve product: %+v", err), http.StatusInternalServerError)
		return
	}
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve currencies: %+v", err), http.StatusInternalServerError)
		return
	}

	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve cart: %+v", err), http.StatusInternalServerError)
		return
	}

	price, err := fe.convertCurrency(r.Context(), &pb.Money{
		Amount:       p.GetPriceUsd(),
		CurrencyCode: defaultCurrency}, currentCurrency(r))
	if err != nil {
		http.Error(w, fmt.Sprintf("failed to convert currency: %+v", err), http.StatusInternalServerError)
		return
	}

	recommendations, err := fe.getRecommendations(r.Context(), sessionID(r), []string{id})
	if err != nil {
		http.Error(w, fmt.Sprintf("failed to get product recommendations: %+v", err), http.StatusInternalServerError)
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
		http.Error(w, "invalid form input", http.StatusBadRequest)
		return
	}
	log.Printf("[addToCart] product_id=%s qty=%d session_id=%+v", productID, quantity, sessionID(r))

	p, err := fe.getProduct(r.Context(), productID)
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve product: %+v", err), http.StatusInternalServerError)
		return
	}

	if err := fe.insertCart(r.Context(), sessionID(r), p.GetId(), int32(quantity)); err != nil {
		http.Error(w, fmt.Sprintf("failed to add to cart: %+v", err), http.StatusInternalServerError)
		return
	}
	w.Header().Set("location", "/cart")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) emptyCartHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[emptyCart] session_id=%+v", sessionID(r))

	if err := fe.emptyCart(r.Context(), sessionID(r)); err != nil {
		http.Error(w, fmt.Sprintf("failed to empty cart: %+v", err), http.StatusInternalServerError)
		return
	}
	w.Header().Set("location", "/")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) viewCartHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[viewCart] session_id=%+v", sessionID(r))
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve currencies: %+v", err), http.StatusInternalServerError)
		return
	}
	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve cart: %+v", err), http.StatusInternalServerError)
		return
	}

	recommendations, err := fe.getRecommendations(r.Context(), sessionID(r), cartIDs(cart))
	if err != nil {
		http.Error(w, fmt.Sprintf("failed to get product recommendations: %+v", err), http.StatusInternalServerError)
		return
	}

	type cartItemView struct {
		Item     *pb.Product
		Quantity int32
		Price    *pb.Money
	}
	items := make([]cartItemView, len(cart))
	for i, item := range cart {
		p, err := fe.getProduct(r.Context(), item.GetProductId())
		if err != nil {
			http.Error(w, fmt.Sprintf("could not retrieve product #%s: %+v", item.GetProductId(), err), http.StatusInternalServerError)
			return
		}
		price, err := fe.convertCurrency(r.Context(), &pb.Money{
			Amount:       p.GetPriceUsd(),
			CurrencyCode: defaultCurrency}, currentCurrency(r))
		if err != nil {
			http.Error(w, fmt.Sprintf("could not convert currency for product #%s: %+v", item.GetProductId(), err), http.StatusInternalServerError)
			return
		}

		multPrice := multMoney(*price.GetAmount(), uint32(item.GetQuantity()))
		items[i] = cartItemView{
			Item:     p,
			Quantity: item.GetQuantity(),
			Price:    &pb.Money{Amount: &multPrice, CurrencyCode: price.GetCurrencyCode()}}
	}

	if err := templates.ExecuteTemplate(w, "cart", map[string]interface{}{
		"user_currency":   currentCurrency(r),
		"currencies":      currencies,
		"session_id":      sessionID(r),
		"recommendations": recommendations,
		"cart_size":       len(cart),
		"items":           items,
	}); err != nil {
		log.Println(err)
	}
}

func (fe *frontendServer) logoutHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[home] session_id=%+v", sessionID(r))
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
	log.Printf("[setCurrency] session_id=%+v code=%s", sessionID(r), cur)
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
