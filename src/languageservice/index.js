const express = require("express");
const { pathOr } = require("ramda");

const translations = require("./translations.json");

const supportedLanguages = ["german", "english"];
const defaultLanguage = "english";

const app = express();
const port = 3000;

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.get("/translate", (req, res) => {
  const { key, language } = req.query;

  const l = supportedLanguages.includes(language) ? language : defaultLanguage;

  const text = pathOr("error", [key, l], translations);

  res.send(text);
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
