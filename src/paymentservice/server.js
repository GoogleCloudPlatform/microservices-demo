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

const path = require('path');
const grpc = require('grpc');
const pino = require('pino');
const protoLoader = require('@grpc/proto-loader');

const charge = require('./charge');
const { tracer } = require('./tracing');

const logger = pino({
  name: 'paymentservice-server',
  messageKey: 'message',
  changeLevelName: 'severity',
  useLevelLabels: true,
  timestamp: pino.stdTimeFunctions.unixTime,
  mixin() {
    const span = tracer.getCurrentSpan()
    if (!span) {
      return {};
    }
    const { traceId, spanId } = span.context();
    return {
      trace_id: traceId.slice(-16), // convert to 64-bit format
      span_id: spanId,
      'service.name': 'paymentservice'
    };
  },
});

class HipsterShopServer {
  constructor(protoRoot, port = HipsterShopServer.PORT) {
    this.port = port;

    this.packages = {
      hipsterShop: this.loadProto(path.join(protoRoot, 'demo.proto')),
      health: this.loadProto(
        path.join(protoRoot, 'grpc/health/v1/health.proto')
      ),
    };

    this.server = new grpc.Server();
    this.loadAllProtos(protoRoot);
  }

  /**
   * Handler for PaymentService.Charge.
   * @param {*} call  { ChargeRequest }
   * @param {*} callback  fn(err, ChargeResponse)
   */
  static ChargeServiceHandler(call, callback) {
    try {
      logger.info(
        `PaymentService#Charge invoked with request ${JSON.stringify(
          call.request
        )}`
      );
      charge(call.request)
        .then((response) => {
          callback(null, response);
        })
        .catch((err) => {
          callback(err);
        });
    } catch (err) {
      console.warn(err);
      callback(err);
    }
  }

  static CheckHandler(call, callback) {
    callback(null, { status: 'SERVING' });
  }

  listen() {
    this.server.bind(
      `0.0.0.0:${this.port}`,
      grpc.ServerCredentials.createInsecure()
    );
    logger.info(`PaymentService grpc server listening on ${this.port}`);
    this.server.start();
  }

  loadProto(path) {
    const packageDefinition = protoLoader.loadSync(path, {
      keepCase: true,
      longs: String,
      enums: String,
      defaults: true,
      oneofs: true,
    });
    return grpc.loadPackageDefinition(packageDefinition);
  }

  loadAllProtos(protoRoot) {
    const hipsterShopPackage = this.packages.hipsterShop.hipstershop;
    const healthPackage = this.packages.health.grpc.health.v1;

    this.server.addService(hipsterShopPackage.PaymentService.service, {
      charge: HipsterShopServer.ChargeServiceHandler.bind(this),
    });

    this.server.addService(healthPackage.Health.service, {
      check: HipsterShopServer.CheckHandler.bind(this),
    });
  }
}

HipsterShopServer.PORT = process.env.PORT;

module.exports = HipsterShopServer;
