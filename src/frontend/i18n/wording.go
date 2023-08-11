package i18n

var (
	wordsMaps = map[string]map[string]string{
		"en": wordsEN,
		"es": wordsES,
		"hi": wordsHI,
		"ja": wordsJA,
		"pt": wordsPT,
	}
)

func GetWord(lang string, key string) string {
	return GetWords(lang)[key]
}

func GetWords(lang string) map[string]string {
	if words, ok := wordsMaps[lang]; ok {
		return words
	}

	return wordsEN
}
