const config = require("../config.json");

module.exports = (req, res) => {
  try {
    console.log("Retrieving supported languages.");
    res.send({ language_codes: config.settings.supportedLanguages });
  } catch (error) {
    console.log("Something went wrong!", error.message);
    res.send({ language_codes: [] });
  }
};
