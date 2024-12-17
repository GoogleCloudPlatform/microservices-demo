const path = require("path");
const grpc = require("grpc");

const PROTO_PATH = path.join(__dirname, "./proto/demo.proto");
const PORT = 7000;

const shopProto = grpc.load(PROTO_PATH).hipstershop;
const client = new shopProto.LanguageService(
  `localhost:${PORT}`,
  grpc.credentials.createInsecure()
);

const request = {
  targetLanguageCode: "de",
  translationKey: "test",
};

client.getSupportedLanguages({}, (err, response) => {
  if (err) {
    console.error(`Error in getSupportedLanguages: ${err}`);
  } else {
    console.log(`Language codes: ${response.language_codes}`);
  }
});

client.translate(request, (err, response) => {
  if (err) {
    console.error(`Error in translate: ${err}`);
  } else {
    console.log(
      `Translate: ${request.translationKey} to ${response.translationResult}`
    );
  }
});
