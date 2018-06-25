package main // import "frontend"

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
	"google.golang.org/grpc"

	pb "frontend/genproto"
)

const (
	port            = "8080"
	defaultCurrency = "USD"
	cookieMaxAge    = 60 * 60 * 48

	cookieSessionID = "session-id"
	cookieCurrency  = "currency"
)

var (
	whitelistedCurrencies = map[string]bool{
		"USD": true, "EUR": true, "CAD": true, "JPY": true}
)

type ctxKeySessionID struct{}

type frontendServer struct {
	productCatalogSvcAddr string
	productCatalogSvcConn *grpc.ClientConn

	cartSvcAddr string
	cartSvcConn *grpc.ClientConn

	currencySvcAddr string
	currencySvcConn *grpc.ClientConn
}

func main() {
	ctx := context.Background()

	srvPort := port
	if os.Getenv("PORT") != "" {
		srvPort = os.Getenv("PORT")
	}
	svc := new(frontendServer)
	// mustMapEnv(&svc.productCatalogSvcAddr, "PRODUCT_CATALOG_SERVICE_ADDR")
	// mustMapEnv(&svc.cartSvcAddr, "CART_SERVICE_ADDR")
	mustMapEnv(&svc.currencySvcAddr, "CURRENCY_SERVICE_ADDR")

	var err error
	svc.currencySvcConn, err = grpc.DialContext(ctx, svc.currencySvcAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("failed to connect currency service: %+v", err)
	}

	r := mux.NewRouter()
	r.HandleFunc("/", svc.ensureSessionID(svc.homeHandler)).
		Methods(http.MethodGet)
	r.HandleFunc("/logout", svc.logoutHandler).
		Methods(http.MethodGet)
	r.HandleFunc("/setCurrency", svc.ensureSessionID(svc.setCurrencyHandler)).
		Methods(http.MethodPost)
	log.Printf("starting server on :" + srvPort)
	log.Fatal(http.ListenAndServe("localhost:"+srvPort, r))
}

func (fe *frontendServer) ensureSessionID(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var sessionID string
		c, err := r.Cookie(cookieSessionID)
		if err == http.ErrNoCookie {
			u, _ := uuid.NewRandom()
			sessionID = u.String()
		} else if err != nil {
			log.Printf("unrecognized cookie error: %+v", err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		} else {
			sessionID = c.Value
		}
		http.SetCookie(w, &http.Cookie{
			Name:   cookieSessionID,
			Value:  sessionID,
			MaxAge: cookieMaxAge,
		})
		ctx := context.WithValue(r.Context(), ctxKeySessionID{}, sessionID)
		r = r.WithContext(ctx)
		next(w, r)
	}
}

func (fe *frontendServer) homeHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[home] session_id=%+v", r.Context().Value(ctxKeySessionID{}))
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	log.Printf("currencies: %+v", currencies)
}

func (fe *frontendServer) logoutHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[home] session_id=%+v", r.Context().Value(ctxKeySessionID{}))
	for _, c := range r.Cookies() {
		c.MaxAge = -1
		http.SetCookie(w, c)
	}
	w.Header().Set("Location", "/")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) setCurrencyHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("[setCurrency] session_id=%+v", r.Context().Value(ctxKeySessionID{}))
	cur := r.FormValue("currency_code")
	if cur != "" {
		http.SetCookie(w, &http.Cookie{
			Name:   cookieCurrency,
			Value:  cur,
			MaxAge: cookieMaxAge,
		})
	}
	w.Header().Set("Location", "/")
	w.WriteHeader(http.StatusFound)
}

func (fe *frontendServer) getCurrencies(ctx context.Context) ([]string, error) {
	currs, err := pb.NewCurrencyServiceClient(fe.currencySvcConn).GetSupportedCurrencies(ctx, &pb.Empty{})
	if err != nil {
		return nil, err
	}
	var out []string
	for _, c := range currs.CurrencyCodes {
		if _, ok := whitelistedCurrencies[c]; ok {
			out = append(out, c)
		}
	}
	return out, nil
}

func mustMapEnv(target *string, envKey string) {
	v := os.Getenv(envKey)
	if v == "" {
		panic(fmt.Sprintf("environment variable %q not set", envKey))
	}
	*target = v
}
