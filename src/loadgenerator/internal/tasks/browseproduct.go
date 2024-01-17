package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/pkg/utils/random"
)

type BrowseProduct struct{}

func (t *BrowseProduct) Perform() error {
	product, err := random.ChoiceString(config.ReadConfig().ProductIDs)
	if err != nil {
		return err
	}

	_, err = config.GetHttpClient().R().Get("/product/" + product)
	if err != nil {
		return err
	}

	return nil
}
