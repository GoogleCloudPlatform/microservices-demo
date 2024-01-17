package tasks

import (
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/go-resty/resty/v2"
)

var server *http.Server

func init() {
	const baseURL = "http://localhost:8080"
	config.SetConfig(baseURL)
	cfg := config.GetConfig()
	cfg.Client = resty.New().SetBaseURL(baseURL)

	handler := http.NewServeMux()
	handler.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/" {
			fmt.Fprintln(w, "Index Page")
			return
		}
		// Catch-all for any other requests on root
		http.Error(w, "Not Found", http.StatusNotFound)
	})

	handler.HandleFunc("/setCurrency", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "Set Currency")
	})

	handler.HandleFunc("/product/", func(w http.ResponseWriter, r *http.Request) {
		productID := strings.TrimPrefix(r.URL.Path, "/product/")
		if productID != "" {
			fmt.Fprintf(w, "Browse Product: %s\n", productID)
			return
		}
		http.Error(w, "Product ID not specified", http.StatusBadRequest)
	})

	handler.HandleFunc("/cart", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			fmt.Fprintln(w, "View Cart")
		case http.MethodPost:
			fmt.Fprintln(w, "Add to Cart")
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	handler.HandleFunc("/cart/checkout", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "Checkout")
	})

	server = &http.Server{
		Addr:    "localhost:8080",
		Handler: handler,
	}

	// Start the test server
	go func() {
		if err := server.ListenAndServe(); err != http.ErrServerClosed {
			log.Fatal("Can't start tests as the server can't start, error: ", err)
		}
	}()
}
