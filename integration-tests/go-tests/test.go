package main

import (
	"fmt"
	"math/rand"
	"time"

	vegeta "github.com/tsenart/vegeta/lib"
)

var (
	baseURL   = "http://10.2.10.105:8080" // Change this to your target URL
	userAgent = "Vegeta Load Tester"
)

func main() {
	rate := vegeta.Rate{Freq: 10, Per: time.Second}
	duration := 1 * time.Minute

	targeter := newCustomTargeter()

	attacker := vegeta.NewAttacker()

	fmt.Println("Testing started...")
	var metrics vegeta.Metrics
	for res := range attacker.Attack(targeter, rate, duration, userAgent) {
		metrics.Add(res)
	}
	metrics.Close()

	fmt.Printf("Mean response time: %.2f ms\n", metrics.Latencies.Mean.Seconds()*1000)
	fmt.Printf("Request rate: %.2f req/s\n", metrics.Rate)
	fmt.Printf("99th percentile response time: %.2f ms\n", metrics.Latencies.P99.Seconds()*1000)
	fmt.Printf("Max response time: %.2f ms\n", metrics.Latencies.Max.Seconds()*1000)
	fmt.Printf("Total requests: %d\n", metrics.Requests)
	fmt.Printf("Total errors: %d\n", metrics.Errors)
}

func newCustomTargeter() vegeta.Targeter {
	return func(tgt *vegeta.Target) error {
		// Implement your own logic for different endpoints and tasks here
		endpoints := []func(*vegeta.Target){
			index,
			setCurrency,
			browseProduct,
			addToCart,
			viewCart,
			checkout,
		}
		task := endpoints[rand.Intn(len(endpoints))]
		task(tgt)
		return nil
	}
}

func index(tgt *vegeta.Target) {
	tgt.Method = "GET"
	tgt.URL = baseURL + "/"
}

func setCurrency(tgt *vegeta.Target) {
	tgt.Method = "POST"
	tgt.URL = baseURL + "/setCurrency"
	tgt.Body = []byte("currency_code=" + randomCurrency())
}

func browseProduct(tgt *vegeta.Target) {
	tgt.Method = "GET"
	tgt.URL = baseURL + "/product/" + randomProduct()
}

func addToCart(tgt *vegeta.Target) {
	tgt.Method = "POST"
	tgt.URL = baseURL + "/cart"
	tgt.Body = []byte(fmt.Sprintf("product_id=%s&quantity=%d", randomProduct(), randomQuantity()))
}

func viewCart(tgt *vegeta.Target) {
	tgt.Method = "GET"
	tgt.URL = baseURL + "/cart"
}

func checkout(tgt *vegeta.Target) {
	tgt.Method = "POST"
	tgt.URL = baseURL + "/cart/checkout"
	tgt.Body = []byte("email=someone@example.com&street_address=1600 Amphitheatre Parkway&zip_code=94043&city=Mountain View&state=CA&country=United States&credit_card_number=4432-8015-6152-0454&credit_card_expiration_month=1&credit_card_expiration_year=2039&credit_card_cvv=672")
}

func randomCurrency() string {
	currencies := []string{"EUR", "USD", "JPY", "CAD"}
	return currencies[rand.Intn(len(currencies))]
}

func randomProduct() string {
	products := []string{
		"0PUK6V6EV0",
		"1YMWWN1N4O",
		"2ZYFJ3GM2N",
		"66VCHSJNUP",
		"6E92ZMYYFZ",
		"9SIQT8TOJO",
		"L9ECAV7KIM",
		"LS4PSXUNUM",
		"OLJCESPC7Z",
	}
	return products[rand.Intn(len(products))]
}

func randomQuantity() int {
	quantities := []int{1, 2, 3, 4, 5, 10}
	return quantities[rand.Intn(len(quantities))]
}
