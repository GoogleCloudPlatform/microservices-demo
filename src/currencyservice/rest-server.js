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
var http = require('http');
var https = require('https');
var privateKey = fs.readFileSync('cert/key.pem', 'utf8');
var certificate = fs.readFileSync('cert/cert.pem', 'utf8');

var credentials = { key: privateKey, cert: certificate };
var express = require('express');
var app = express();
var common = require('./common.js')

app.get('/convert', function(req, res) {
  var from = req.query.from
  var units = req.query.units
  var nanos = req.query.nanos
  var to_code = req.query.to_code
  const call = {
    request: {
      from: { currency_code: from, units: units, nanos: nanos },
      to_code: to_code,
    }
  }
  common.convert(call, (err, data) => {
    const a = err
    res.send(data)
    console.log(data);
  });
})

app.get('/list-supported-currencies', function(req, res) {
  common.getCurrencyData((data => {
    data = Object.keys(data)
    res.send(data);
  }));
})

restPort = process.env.REST_PORT;
// var httpServer = http.createServer(app);
var httpsServer = https.createServer(credentials, app);
console.log("CurrencyService rest server started on port: " + restPort);
httpsServer.listen(restPort);
