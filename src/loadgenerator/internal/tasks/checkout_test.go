package tasks

import (
	"testing"

	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/pkg/utils/random"
	"github.com/stretchr/testify/assert"
)

func TestCheckout_Perform_Success(t *testing.T) {
	quantity, err := random.ChoiceInt(config.GetConfig().Quantity)
	assert.Nil(t, err)

	product, err := random.ChoiceString(config.GetConfig().ProductIDs)
	assert.Nil(t, err)

	data := AddToCart{
		ProductID: product,
		Quantity:  quantity,
	}
	err = data.Perform()
	assert.Nil(t, err)

	checkout := &Checkout{
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
	err = checkout.Perform()

	assert.Nil(t, err)
}
