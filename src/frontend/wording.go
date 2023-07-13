package main

func renderWording(requestedLanguage string, key string) string {
	// Spanish
	if requestedLanguage == "es" {
		return wordingEs[key]
	}
	// Default to English
	return wordingEn[key]
}
