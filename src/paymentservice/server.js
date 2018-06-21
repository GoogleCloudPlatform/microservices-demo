const grpc = require('grpc');
const protoLoader = require('@grpc/proto-loader');

class HipsterShopServer {
  constructor(protoFile, port = HipsterShopServer.DEFAULT_PORT) {
    this.port = port;

    this.server = new grpc.Server();
    this.loadProto(protoFile);
  }

  /**
   * Handler for PaymentService.Charge.
   * @param {*} call  { ChargeRequest }
   * @param {*} callback  fn(err, ChargeResponse)
   */
  static ChargeServiceHandler(call, callback) {
    try {
      const response = this.charge(call.request)
      callback(null, response);
    } catch (err) {
      callback(err);
    }
  }

  /**
   * Charge function
   * @param {*} request
   * @return transaction_id
   */
  static charge(request) {
    return { transaction_id: -1 }
  }

  listen() {
    this.server.bind(`0.0.0.0:${this.port}`, grpc.ServerCredentials.createInsecure());
    this.server.start();
  }

  loadProto(path) {
    const packageDefinition = protoLoader.loadSync(
      path,
      {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true,
      },
    );
    const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
    const hipsterShopPackage = protoDescriptor.hipstershop;

    this.addProtoService(hipsterShopPackage.PaymentService.service);
  }

  addProtoService(service) {
    this.server.addService(
      service,
      {
        charge: HipsterShopServer.ChargeServiceHandler.bind(this),
      },
    );
  }
}

HipsterShopServer.DEFAULT_PORT = 50051;

module.exports = HipsterShopServer;
