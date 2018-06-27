/*
 *
 * Copyright 2015 gRPC authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

const path = require('path');
const grpc = require('grpc');

const PROTO_PATH = path.join(__dirname, './proto/demo.proto');
const PORT = 31337;

const shopProto = grpc.load(PROTO_PATH).hipstershop;
const client = new shopProto.CurrencyService(`localhost:${PORT}`,
  grpc.credentials.createInsecure());

const request = {
  from: {
    currency_code: 'USD',
    units: 300,
    nanos: 500000000
  },
  to_code: 'CHF'
};

function _moneyToString (m) {
  return `${m.amount.decimal}.${m.amount.fractional} ${m.currency_code}`;
}

client.getSupportedCurrencies({}, (err, response) => {
  if (err) {
    console.error(`Error in getSupportedCurrencies: ${err}`);
  } else {
    console.log(`Currency codes: ${response.currency_codes}`);
  }
});

client.convert(request, function (err, response) {
  if (err) {
    console.error(`Error in convert: ${err}`);
  } else {
    console.log(`Convert: ${_moneyToString(request.from)} to ${_moneyToString(response)}`);
  }
});
