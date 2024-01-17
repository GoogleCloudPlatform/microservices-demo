package config

import (
	"github.com/go-resty/resty/v2"
)

type Config struct {
	ProductIDs    []string
	CurrencyCodes []string
	Choices       []int
	MaxWaitTime   int
	Client        *resty.Client
	HostName      string
}

func ReadConfig() *Config {
	return &Config{
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
		Choices:       []int{1, 2, 3, 4, 5, 10},
		MaxWaitTime:   10,
		Client:        resty.New().SetBaseURL("http://example.com"), // TODO: replace with flag
	}
}

func GetHttpClient() *resty.Client {
	return ReadConfig().Client
}
