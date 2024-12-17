const express = require("express");

const config = require("./config.json");

const { translate, getSupportedLanguages } = require("./resolvers");

const app = express();

const PORT = process.env.PORT || config.service.port;
const SERVICE_NAME = config.service.name;

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.get("/getSupportedLanguages", (req, res) =>
  getSupportedLanguages(req, res)
);

app.post("/translate", (req, res) => translate(req, res));

app.listen(PORT, () => {
  console.log(`${SERVICE_NAME} listening on port ${PORT}`);
});
