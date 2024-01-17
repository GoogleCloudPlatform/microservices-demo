package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/sirupsen/logrus"
)

type Checkout struct {
	Email                     string `json:"email"`
	StreetAddress             string `json:"street_address"`
	ZipCode                   string `json:"zip_code"`
	City                      string `json:"city"`
	State                     string `json:"state"`
	Country                   string `json:"country"`
	CreditCardNumber          string `json:"credit_card_number"`
	CreditCardExpirationMonth string `json:"credit_card_expiration_month"`
	CreditCardExpirationYear  string `json:"credit_card_expiration_year"`
	CreditCardCVV             string `json:"credit_card_cvv"`
}

func (t *Checkout) Perform() error {
	logrus.Debugf("Checkout.Perform()")
	addToCart := AddToCart{}
	err := addToCart.Perform()
	if err != nil {
		return err
	}

	checkoutInfo := Checkout{
		Email:                     "someone@example.com",
		StreetAddress:             "1600 Amphitheatre Parkway",
		ZipCode:                   "94043",
		City:                      "Mountain View",
		State:                     "CA",
		Country:                   "United States",
		CreditCardNumber:          "4432-8015-6152-0454",
		CreditCardExpirationMonth: "1",
		CreditCardExpirationYear:  "2039",
		CreditCardCVV:             "672",
	}

	_, err = config.GetHttpClient().R().SetBody(checkoutInfo).Post("/cart/checkout")
	if err != nil {
		return err
	}

	return nil
}
