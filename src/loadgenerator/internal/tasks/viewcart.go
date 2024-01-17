package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/sirupsen/logrus"
)

type ViewCart struct{}

// Perform executes the ViewCart task.
// It sends a GET request to the "/cart" endpoint using the configured HTTP client.
// Returns an error if the request fails.
func (t *ViewCart) Perform() error {
	logrus.Debugf("ViewCart.Perform()")
	_, err := config.GetHttpClient().R().Get("/cart")
	if err != nil {
		return err
	}

	return nil
}
