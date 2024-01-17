package tasks

import "github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"

type Index struct{}

func (t *Index) Perform() error {
	_, err := config.GetHttpClient().R().Get("/")
	if err != nil {
		return err
	}

	return nil
}
