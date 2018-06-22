/*
 * Copyright 2018 Google LLC.
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
 */

const path = require('path');
const grpc = require('grpc');
const request = require('request');
const xml2js = require('xml2js');

const PROTO_PATH = path.join(__dirname, './proto/demo.proto');
const PORT = 31337;
const DATA_URL = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml';
const shopProto = grpc.load(PROTO_PATH).hipstershop;

/**
 * Helper function that gets currency data from an XML webpage
 * Uses public data from European Central Bank
 */
function _getCurrencyData (callback) {
  request(DATA_URL, (err, res) => {
    if (err) {
      throw new Error(`Error getting data: ${err}`);
    }

    const body = res.body.split('\n').slice(7, -2).join('\n');
    xml2js.parseString(body, (err, resJs) => {
      if (err) {
        throw new Error(`Error parsing HTML: ${err}`);
      }

      const array = resJs['Cube']['Cube'].map(x => x['$']);
      const results = array.reduce((acc, x) => {
        acc[x['currency']] = x['rate'];
        return acc;
      }, { 'EUR': '1.0' });
      callback(results);
    });
  });
}

/**
 * Helper function that handles decimal/fractional carrying
 */
function _carry (amount) {
  amount.fractional += (amount.decimal % 1) * 100;
  amount.decimal = Math.floor(amount.decimal) + Math.floor(amount.fractional / 100);
  amount.fractional = amount.fractional % 100;
  return amount;
}

/**
 * Lists the supported currencies
 */
function getSupportedCurrencies (call, callback) {
  _getCurrencyData((data) => {
    callback(null, {currency_codes: Object.keys(data)});
  });
}

/**
 * Converts between currencies
 */
function convert (call, callback) {
  try {
    _getCurrencyData((data) => {
      const request = call.request;

      // Convert: from_currency --> EUR
      const from = request.from;
      const euros = _carry({
        decimal: from.amount.decimal / data[from.currency_code],
        fractional: from.amount.fractional / data[from.currency_code]
      });

      // Convert: EUR --> to_currency
      const target = _carry({
        decimal: euros.decimal * data[request.to_code],
        fractional: euros.fractional * data[request.to_code]
      });
      target.fractional = Math.round(target.fractional);

      callback(null, {currency_code: request.to_code, amount: target});
    });
  } catch (err) {
    callback(err.message);
  }
}

/**
 * Starts an RPC server that receives requests for the
 * CurrencyConverter service at the sample server port
 */
function main () {
  const server = new grpc.Server();
  server.addService(shopProto.CurrencyService.service, {getSupportedCurrencies, convert});
  server.bind(`0.0.0.0:${PORT}`, grpc.ServerCredentials.createInsecure());
  server.start();
}

main();
