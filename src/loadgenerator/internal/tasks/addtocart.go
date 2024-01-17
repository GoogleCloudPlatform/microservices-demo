package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/pkg/utils/random"
	"github.com/sirupsen/logrus"
)

type AddToCart struct {
	ProductID string `json:"product_id"`
	Quantity  int    `json:"quantity"`
}

// Perform executes the AddToCart task by randomly selecting a quantity and a product ID,
// and then making an HTTP GET request to retrieve the product information.
// It then adds the selected product to the cart by making an HTTP POST request to the cart endpoint.
// Returns an error if any of the operations fail.
func (t *AddToCart) Perform() error {
	quantity, err := random.ChoiceInt(config.GetConfig().Quantity)
	if err != nil {
		return err
	}

	product, err := random.ChoiceString(config.GetConfig().ProductIDs)
	if err != nil {
		return err
	}

	logrus.Debugf("AddToCart task with product_id=%s, quantity=%d", t.ProductID, t.Quantity)

	_, err = config.GetHttpClient().R().Get("/product/" + product)
	if err != nil {
		return err
	}

	data := AddToCart{
		ProductID: product,
		Quantity:  quantity,
	}
	_, err = config.GetHttpClient().R().SetBody(data).Post("/cart")
	if err != nil {
		return err
	}

	return nil
}
