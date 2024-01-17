package config

import (
	"github.com/go-resty/resty/v2"
	"github.com/sirupsen/logrus"
)

var config *Config

type Config struct {
	ProductIDs    []string
	CurrencyCodes []string
	Quantity      []int
	MaxWaitTime   int
	Client        *resty.Client
	HostName      string
}

func SetConfig(baseURL string) *Config {
	config = &Config{
		ProductIDs: []string{
			"0PUK6V6EV0",
			"1YMWWN1N4O",
			"2ZYFJ3GM2N",
			"66VCHSJNUP",
			"6E92ZMYYFZ",
			"9SIQT8TOJO",
			"L9ECAV7KIM",
			"LS4PSXUNUM",
			"OLJCESPC7Z",
		},
		CurrencyCodes: []string{"EUR", "USD", "JPY", "CAD"},
		Quantity:      []int{1, 2, 3, 4, 5, 10},
		MaxWaitTime:   10,
		Client:        resty.New().SetBaseURL(baseURL),
	}

	logrus.Info("Setting config done")
	return config
}

func GetConfig() *Config {
	return config
}

func GetHttpClient() *resty.Client {
	return config.Client
}
