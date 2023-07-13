package main

func getRenderWordingFunc(languageIsoCode string) func(string) string {
	// Spanish
	if languageIsoCode == "es" {
		return func(key string) string { return wordingEs[key] }
	}
	// Default to English
	return func(key string) string { return wordingEn[key] }
}
