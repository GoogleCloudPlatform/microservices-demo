package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
	"google.golang.org/grpc"
)

const (
	port            = "8080"
	defaultCurrency = "USD"
	cookieMaxAge    = 60 * 60 * 48

	cookiePrefix    = "shop_"
	cookieSessionID = cookiePrefix + "session-id"
	cookieCurrency  = cookiePrefix + "currency"
)

var (
	whitelistedCurrencies = map[string]bool{
		"USD": true, "EUR": true, "CAD": true, "JPY": true}
)

type ctxKeySessionID struct{}

type frontendServer struct {
	productCatalogSvcAddr string
	productCatalogSvcConn *grpc.ClientConn

	currencySvcAddr string
	currencySvcConn *grpc.ClientConn

	cartSvcAddr string
	cartSvcConn *grpc.ClientConn

	recommendationSvcAddr string
	recommendationSvcConn *grpc.ClientConn

	checkoutSvcAddr string
	checkoutSvcConn *grpc.ClientConn

	shippingSvcAddr string
	shippingSvcConn *grpc.ClientConn
}

func main() {
	ctx := context.Background()
	log.SetFlags(log.Lshortfile | log.Ltime)

	srvPort := port
	if os.Getenv("PORT") != "" {
		srvPort = os.Getenv("PORT")
	}
	svc := new(frontendServer)
	mustMapEnv(&svc.productCatalogSvcAddr, "PRODUCT_CATALOG_SERVICE_ADDR")
	mustMapEnv(&svc.currencySvcAddr, "CURRENCY_SERVICE_ADDR")
	mustMapEnv(&svc.cartSvcAddr, "CART_SERVICE_ADDR")
	mustMapEnv(&svc.recommendationSvcAddr, "RECOMMENDATION_SERVICE_ADDR")
	mustMapEnv(&svc.checkoutSvcAddr, "CHECKOUT_SERVICE_ADDR")
	mustMapEnv(&svc.shippingSvcAddr, "SHIPPING_SERVICE_ADDR")

	var err error
	svc.currencySvcConn, err = grpc.DialContext(ctx, svc.currencySvcAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("failed to connect currency service: %+v", err)
	}
	svc.productCatalogSvcConn, err = grpc.DialContext(ctx, svc.productCatalogSvcAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("failed to connect productcatalog service: %+v", err)
	}
	svc.cartSvcConn, err = grpc.DialContext(ctx, svc.cartSvcAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("failed to connect cart service at %s: %+v", svc.cartSvcAddr, err)
	}
	svc.recommendationSvcConn, err = grpc.DialContext(ctx, svc.recommendationSvcAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("failed to connect recommendation service at %s: %+v", svc.recommendationSvcAddr, err)
	}
	svc.shippingSvcConn, err = grpc.DialContext(ctx, svc.shippingSvcAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("failed to connect shipping service at %s: %+v", svc.shippingSvcAddr, err)
	}
	svc.checkoutSvcConn, err = grpc.DialContext(ctx, svc.checkoutSvcAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("failed to connect checkout service at %s: %+v", svc.checkoutSvcAddr, err)
	}

	r := mux.NewRouter()
	r.HandleFunc("/", ensureSessionID(svc.homeHandler)).Methods(http.MethodGet, http.MethodHead)
	r.HandleFunc("/product/{id}", ensureSessionID(svc.productHandler)).Methods(http.MethodGet, http.MethodHead)
	r.HandleFunc("/cart", ensureSessionID(svc.viewCartHandler)).Methods(http.MethodGet, http.MethodHead)
	r.HandleFunc("/cart", ensureSessionID(svc.addToCartHandler)).Methods(http.MethodPost)
	r.HandleFunc("/cart/empty", ensureSessionID(svc.emptyCartHandler)).Methods(http.MethodPost)
	r.HandleFunc("/setCurrency", ensureSessionID(svc.setCurrencyHandler)).Methods(http.MethodPost)
	r.HandleFunc("/logout", svc.logoutHandler).Methods(http.MethodGet)
	r.HandleFunc("/cart/checkout", ensureSessionID(svc.placeOrderHandler)).Methods(http.MethodPost)
	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static/"))))
	log.Printf("starting server on :" + srvPort)
	log.Fatal(http.ListenAndServe(":"+srvPort, r))
}

func mustMapEnv(target *string, envKey string) {
	v := os.Getenv(envKey)
	if v == "" {
		panic(fmt.Sprintf("environment variable %q not set", envKey))
	}
	*target = v
}
