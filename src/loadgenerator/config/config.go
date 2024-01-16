package config

type Config struct {
	ProductIDs    []string
	CurrencyCodes []string
	MaxWaitTime   int
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
		MaxWaitTime:   10,
	}
}
