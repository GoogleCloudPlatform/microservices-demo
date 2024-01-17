package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/sirupsen/logrus"
)

type Index struct{}

// Perform executes the task of sending a GET request to the root endpoint ("/") for the index.
// It uses the configured HTTP client to make the request.
// Returns an error if the request fails.
func (t *Index) Perform() error {
	logrus.Debugf("Index.Perform()")
	_, err := config.GetHttpClient().R().Get("/")
	if err != nil {
		return err
	}

	return nil
}
