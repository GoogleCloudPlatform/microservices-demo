package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/pkg/utils/random"
)

type SetCurrency struct {
	CurrencyCode string `json:"currency_code"`
}

func (t *SetCurrency) Perform() error {
	currency, err := random.ChoiceString(config.ReadConfig().CurrencyCodes)
	if err != nil {
		return err
	}

	data := SetCurrency{
		CurrencyCode: currency,
	}
	_, err = config.GetHttpClient().R().SetBody(data).Post("/setCurrency")
	if err != nil {
		return err
	}

	return nil
}
