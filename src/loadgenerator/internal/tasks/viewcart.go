package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/sirupsen/logrus"
)

type ViewCart struct{}

func (t *ViewCart) Perform() error {
	logrus.Debugf("ViewCart.Perform()")
	_, err := config.GetHttpClient().R().Get("/cart")
	if err != nil {
		return err
	}

	return nil
}
