package i18n

func RenderWording(lang string, key string) string {
	wordsMaps := map[string]map[string]string{
		"en": wordsEN,
		"es": wordsES,
		"hi": wordsHI,
		"ja": wordsJA,
		"pt": wordsPT,
	}

	if words, ok := wordsMaps[lang]; ok {
		return words[key]
	}

	return wordsEN[key]
}
