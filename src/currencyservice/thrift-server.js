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
var currencySvc = require('./thriftjs/CurrencyService.js');
var common = require('./common.js');

var currencyHandler = {
  GetSupportedCurrencies: function(result) {
    common.getCurrencyData((data => {
      data = Object.keys(data)
      result(data)
    }));
  },
  Convert: function(money, to_curr, result) {
    const call = {
      request: {
        from: money,
        to_code: to_curr,
      }
    }
    var reult = {}
    common.convert(call, (err, data) => {
      const a = err
      result(data)
    });
  }
};

var transports = {
  'buffered': thrift.TBufferedTransport,
  'framed': thrift.TFramedTransport
};

var protocols = {
  'json': thrift.TJSONProtocol,
  'binary': thrift.TBinaryProtocol,
  'compact': thrift.TCompactProtocol
};

var serverOpt = {
  transport: thrift.TBufferedTransport,
  protocol: thrift.TBinaryProtocol,
  key: fs.readFileSync('./cert/cert.pem'),
  cert: fs.readFileSync('./cert/key.pem'),
}


thriftPort = process.env.THRIFT_PORT;

var s = thrift.createServer(currencySvc, currencyHandler, serverOpt).on('error', function(error) { console.log(error); }) //.listen(thriftPort);
s.listen(thriftPort)
console.log("CurrencyService thrift server started on port: " + thriftPort);
