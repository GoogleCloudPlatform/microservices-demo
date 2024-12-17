const config = require("./config.json");
const translations = require("./translations.json");
const { pathOr, isEmpty } = require("ramda");

const path = require("path");
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");

const MAIN_PROTO_PATH = path.join(__dirname, "./proto/demo.proto");
const HEALTH_PROTO_PATH = path.join(
  __dirname,
  "./proto/grpc/health/v1/health.proto"
);

const PORT = process.env.PORT;

const shopProto = _loadProto(MAIN_PROTO_PATH).hipstershop;
const healthProto = _loadProto(HEALTH_PROTO_PATH).grpc.health.v1;

/**
 * Helper function that loads a protobuf file.
 */
function _loadProto(path) {
  const packageDefinition = protoLoader.loadSync(path, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
  });
  return grpc.loadPackageDefinition(packageDefinition);
}

/**
 * Lists the supported languages
 */
const getSupportedLanguages = (call, callback) =>
  callback(config.settings.supportedLanguages);

/**
 * Get translation using translation key and target language code
 */
const translate = (call, callback) => {
  try {
    const { translationKey, targetLanguageCode } = call.request;

    const translationResult = pathOr(
      "",
      [translationKey, targetLanguageCode],
      translations
    );

    if (isEmpty(translationResult)) {
      throw new Error(
        `Translation for key ${translationKey} and target language ${targetLanguageCode} not found!`
      );
    }

    const result = {
      languageCode: targetLanguageCode,
      translationResult,
    };

    console.log(`translation request successful`);
    callback(null, result);
  } catch (err) {
    console.error(`translation request failed: ${err}`);
    callback(err.message);
  }
};

/**
 * Endpoint for health checks
 */
function check(call, callback) {
  callback(null, { status: "SERVING" });
}

/**
 * Starts an RPC server that receives requests for the
 * Language service at the sample server port
 */
function main() {
  console.log(`Starting gRPC server on port ${PORT}...`);
  const server = new grpc.Server();
  server.addService(shopProto.LanguageService.service, {
    getSupportedLanguages,
    translate,
  });
  server.addService(healthProto.Health.service, { check });

  server.bindAsync(
    `[::]:${PORT}`,
    grpc.ServerCredentials.createInsecure(),
    function () {
      console.log(`LanguageService gRPC server started on port ${PORT}`);
      server.start();
    }
  );
}

main();
