package main

import (
	"context"
	"fmt"
	"html/template"
	"log"
	"net/http"
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
	log.Printf("[home] session_id=%+v", r.Context().Value(ctxKeySessionID{}))
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	products, err := fe.getProducts(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
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
		"session_id":    r.Context().Value(ctxKeySessionID{}),
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
	log.Printf("[productHandler] id=%s currency=%s", id, currentCurrency(r))
	p, err := fe.getProduct(r.Context(), id)
	if err != nil {
		http.Error(w, fmt.Sprintf("could not retrieve product: %+v", err), http.StatusInternalServerError)
		return
	}

	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	price, err := fe.convertCurrency(r.Context(), &pb.Money{
		Amount:       p.GetPriceUsd(),
		CurrencyCode: defaultCurrency}, currentCurrency(r))
	if err != nil {
		http.Error(w, fmt.Sprintf("failed to convert currency: %+v", err), http.StatusInternalServerError)
		return
	}

	product := struct {
		Item  *pb.Product
		Price *pb.Money
	}{p, price}

	if err := templates.ExecuteTemplate(w, "product", map[string]interface{}{
		"user_currency": currentCurrency(r),
		"currencies":    currencies,
		"product":       product,
		"session_id":    r.Context().Value(ctxKeySessionID{}),
	}); err != nil {
		log.Println(err)
	}
}

func (fe *frontendServer) logoutHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[home] session_id=%+v", r.Context().Value(ctxKeySessionID{}))
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
	log.Printf("[setCurrency] session_id=%+v code=%s", r.Context().Value(ctxKeySessionID{}), cur)
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
