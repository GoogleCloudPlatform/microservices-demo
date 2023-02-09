/*
 * Copyright 2022 Skyramp, Inc.
 *
 *	Licensed under the Apache License, Version 2.0 (the "License");
 *	you may not use this file except in compliance with the License.
 *	You may obtain a copy of the License at
 *
 *	http://www.apache.org/licenses/LICENSE-2.0
 *
 *	Unless required by applicable law or agreed to in writing, software
 *	distributed under the License is distributed on an "AS IS" BASIS,
 *	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *	See the License for the specific language governing permissions and
 *	limitations under the License.
*/
const { parentPort, data } = require("worker_threads");
var fs = require('fs');
var thrift = require('thrift');
var paymentSvc = require('./thrift-nodejs/PaymentService.js');
var charge = require('./charge');

var paymentHandler = {
  Charge: function(amount, creditCard, result) {
    console.log("Received charge")
    request = { "amount": amount, "credit_card": creditCard, };
    id = charge(request)
    result(null, id.transaction_id);
  }
};

var paymentSrvOpt = {
  handler: paymentHandler,
  processor: paymentSvc,
  protocol: thrift.TBinaryProtocol,
  transport: thrift.TBufferedTransport
};

var serverOpt = {
 services: {
  "/PaymentService": paymentSrvOpt
 }
}

thriftPort =  process.env.THRIFT_PORT;
var s = thrift.createWebServer(serverOpt).listen(thriftPort);
console.log("Thrift Server running on port: " + thriftPort);
