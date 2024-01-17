package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/pkg/utils/random"
)

type AddToCart struct {
	ProductID string `json:"product_id"`
	Quantity  int    `json:"quantity"`
}

func (t *AddToCart) Perform() error {
	choice, err := random.ChoiceInt(config.ReadConfig().Choices)
	if err != nil {
		return err
	}

	product, err := random.ChoiceString(config.ReadConfig().ProductIDs)
	if err != nil {
		return err
	}

	_, err = config.GetHttpClient().R().Get("/product/" + product)
	if err != nil {
		return err
	}

	data := AddToCart{
		ProductID: product,
		Quantity:  choice,
	}
	_, err = config.GetHttpClient().R().SetBody(data).Post("/cart")
	if err != nil {
		return err
	}

	return nil

	return nil
}
