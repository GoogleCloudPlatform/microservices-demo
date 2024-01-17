package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/sirupsen/logrus"
)

type Index struct{}

func (t *Index) Perform() error {
	logrus.Debugf("Index.Perform()")
	_, err := config.GetHttpClient().R().Get("/")
	if err != nil {
		return err
	}

	return nil
}
