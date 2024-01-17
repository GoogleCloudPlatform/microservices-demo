package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/pkg/utils/random"
	"github.com/sirupsen/logrus"
)

type BrowseProduct struct{}

// Perform performs the browse product task.
// It selects a random product ID from the configuration and sends a GET request to the corresponding product endpoint.
// Returns an error if there is any issue with selecting the product ID or sending the request.
func (t *BrowseProduct) Perform() error {
	logrus.Debugf("BrowseProduct.Perform()")
	product, err := random.ChoiceString(config.GetConfig().ProductIDs)
	if err != nil {
		return err
	}

	_, err = config.GetHttpClient().R().Get("/product/" + product)
	if err != nil {
		return err
	}

	return nil
}
