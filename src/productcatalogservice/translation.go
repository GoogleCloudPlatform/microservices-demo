package main

import (
	"context"
	"fmt"

	translate "cloud.google.com/go/translate/apiv3"
	"cloud.google.com/go/translate/apiv3/translatepb"
)

// A function that translates a list of strings from English to multiple different languages
func translateStrings(ctx context.Context, projectID, targetLangCode string, strings []string) ([]string, error) {
	// return strings, nil // TODO: REMOVE THIS LINE! REMOVE THIS LINE! REMOVE THIS LINE! REMOVE THIS LINE! REMOVE THIS LINE! REMOVE THIS LINE!
	// Create a client for Cloud Translation API.
	client, err := translate.NewTranslationClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("NewTranslationClient: %w", err)
	}
	defer client.Close()

	// Create a request.
	request := &translatepb.TranslateTextRequest{
		Parent:             fmt.Sprintf("projects/%s/locations/global", projectID),
		TargetLanguageCode: targetLangCode,
		Contents:           strings,
		MimeType:           "text/plain",
	}

	// Translate the strings.
	response, err := client.TranslateText(ctx, request)
	if err != nil {
		return nil, fmt.Errorf("TranslateText: %w", err)
	}

	// Return the translated strings.
	translatedStrings := make([]string, len(strings))
	for i, translation := range response.GetTranslations() {
		translatedStrings[i] = translation.GetTranslatedText()
	}
	return translatedStrings, nil
}
