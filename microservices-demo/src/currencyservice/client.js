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
require('@google-cloud/trace-agent').start();

const path = require('path');
const grpc = require('grpc');
const pino = require('pino');

const PROTO_PATH = path.join(__dirname, './proto/demo.proto');
const PORT = 7000;

const shopProto = grpc.load(PROTO_PATH).hipstershop;
const client = new shopProto.CurrencyService(`localhost:${PORT}`,
  grpc.credentials.createInsecure());

const logger = pino({
  name: 'currencyservice-client',
  messageKey: 'message',
  formatters: {
    level (logLevelString, logLevelNum) {
      return { severity: logLevelString }
    }
  }
});

const request = {
  from: {
    currency_code: 'CHF',
    units: 300,
    nanos: 0
  },
  to_code: 'EUR'
};

function _moneyToString (m) {
  return `${m.units}.${m.nanos.toString().padStart(9,'0')} ${m.currency_code}`;
}

client.getSupportedCurrencies({}, (err, response) => {
  if (err) {
    logger.error(`Error in getSupportedCurrencies: ${err}`);
  } else {
    logger.info(`Currency codes: ${response.currency_codes}`);
  }
});

client.convert(request, (err, response) => {
  if (err) {
    logger.error(`Error in convert: ${err}`);
  } else {
    logger.log(`Convert: ${_moneyToString(request.from)} to ${_moneyToString(response)}`);
  }
});
