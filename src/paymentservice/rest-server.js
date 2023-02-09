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
const charge = require('./charge');
var express = require('express');
var app = express();
app.use(express.json())

app.post('/charge', function(req, res) {
  res.json(charge(req.body));
})

restPort = process.env.REST_PORT;

app.listen(restPort, () => {
  console.log(`Rest server started on on port ${restPort}`)
})
