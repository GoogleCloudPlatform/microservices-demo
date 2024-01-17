package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/pkg/utils/random"
	"github.com/sirupsen/logrus"
)

type SetCurrency struct {
	CurrencyCode string `json:"currency_code"`
}

func (t *SetCurrency) Perform() error {
	logrus.Debugf("SetCurrency.Perform()")
	currency, err := random.ChoiceString(config.GetConfig().CurrencyCodes)
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
