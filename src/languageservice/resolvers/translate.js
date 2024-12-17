const translations = require("../translations.json");
const { settings } = require("../config.json");

const { isEmpty, pathOr } = require("ramda");

module.exports = (req, res) => {
  try {
    const { translationKey, targetLanguageCode } = req;
    const { supportedLanguages, defaults } = settings;

    const langCode = supportedLanguages.includes(targetLanguageCode)
      ? targetLanguageCode
      : defaults.language;

    const result = pathOr("", [translationKey, langCode], translations);

    if (isEmpty(result)) {
      throw new Error(
        `Translation for key ${translationKey} and target language ${targetLanguageCode} not found!`
      );
    }

    console.log("Translation request successful");

    res.send(result);
  } catch (err) {
    console.error(`Translation request failed: ${err}`);
    res.send(settings.defaults.errorText);
  }
};
