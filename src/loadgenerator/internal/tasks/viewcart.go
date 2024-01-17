package tasks

import "github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"

type ViewCart struct{}

func (t *ViewCart) Perform() error {
	_, err := config.GetHttpClient().R().Get("/cart")
	if err != nil {
		return err
	}

	return nil
}
