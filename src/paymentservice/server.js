// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

const grpc = require('grpc');
const protoLoader = require('@grpc/proto-loader');

const charge = require('./charge');

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
      console.log(`PaymentService#Charge invoked with request ${JSON.stringify(call.request)}`)
      const response = charge(call.request)
      callback(null, response);
    } catch (err) {
      console.warn(err);
      callback(err);
    }
  }

  listen() {
    this.server.bind(`0.0.0.0:${this.port}`, grpc.ServerCredentials.createInsecure());
    console.log(`PaymentService grpc server listening on ${this.port}`);
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
