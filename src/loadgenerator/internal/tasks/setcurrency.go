package tasks

import (
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/pkg/utils/random"
	"github.com/sirupsen/logrus"
)

type SetCurrency struct {
	CurrencyCode string `json:"currency_code"`
}

// Perform performs the task of setting a random currency code.
// It chooses a random currency code from the configuration and sends a POST request to the "/setCurrency" endpoint.
// Returns an error if there is any issue in choosing the currency code or sending the request.
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
