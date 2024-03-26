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

const cardValidator = require('simple-card-validator');
const { v4: uuidv4 } = require('uuid');
const pino = require('pino');

const logger = pino({
  name: 'paymentservice-charge',
  messageKey: 'message',
  formatters: {
    level (logLevelString, logLevelNum) {
      return { severity: logLevelString }
    }
  }
});


class CreditCardError extends Error {
  constructor (message) {
    super(message);
    this.code = 400; // Invalid argument error
  }
}

class InvalidCreditCard extends CreditCardError {
  constructor (cardType) {
    super(`Credit card info is invalid`);
  }
}

class UnacceptedCreditCard extends CreditCardError {
  constructor (cardType) {
    super(`Sorry, we cannot process ${cardType} credit cards. Only VISA or MasterCard is accepted.`);
  }
}

class ExpiredCreditCard extends CreditCardError {
  constructor (number, month, year) {
    super(`Your credit card (ending ${number.substr(-4)}) expired on ${month}/${year}`);
  }
}

async function exampleFetch() {
    const response = await fetch('http://google.com');
    const json = await response.json();
    logger.info(json);
}


/**
 * Verifies the credit card number and (pretend) charges the card.
 *
 * @param {*} request
 * @return transaction_id - a random uuid.
 */
module.exports = function charge (request) {
  const { amount, credit_card: creditCard } = request;
  const cardNumber = creditCard.credit_card_number;
  const cardInfo = cardValidator(cardNumber);
  const {
    card_type: cardType,
    valid
  } = cardInfo.getCardDetails();

  /*
  const requestf = async () => {
    const response = await fetch('http://google.com/');
    const json = await response.json();
    console.log("testing only: " + json);
}

requestf();
*/

  //exampleFetch();

  if (!valid) { throw new InvalidCreditCard(); }

  // Only VISA and mastercard is accepted, other card types (AMEX, dinersclub) will
  // throw UnacceptedCreditCard error.
  if (!(cardType === 'visa' || cardType === 'mastercard')) { throw new UnacceptedCreditCard(cardType); }

  // Also validate expiration is > today.
  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();
  const { credit_card_expiration_year: year, credit_card_expiration_month: month } = creditCard;
  if ((currentYear * 12 + currentMonth) > (year * 12 + month)) { throw new ExpiredCreditCard(cardNumber.replace('-', ''), month, year); }

  logger.info(`Transaction info received : ${cardType} ending ${cardNumber.substr(-4)} \
    Amount: ${amount.currency_code}${amount.units}.${amount.nanos}`);

  var data = {};
  data.amount_money = {};
  data.amount_money.amount = Number(amount.units) ;


  data.amount_money.currency = amount.currency_code;
  var timeNow = Date.now();
  data.idempotency_key = timeNow.toString() + amount.currency_code + amount.units + amount.nanos;
  data.source_id = "cnon:card-nonce-ok";

  logger.info(`Transaction to be processed by  a pos:  ${cardType} ending ${cardNumber.substr(-4)} \
    data: ${JSON.stringify(data)}`);

  var response = {};
   // Send the POST request using fetch
  const requestFunc = async () => {
  const response3 = await fetch("https://connect.squareupsandbox.com/v2/payments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Square-Version": "2024-02-22",
      "Authorization": "Bearer EAAAlz9wqEc5MUwJ4Yrok9tTOv6X4lHEuSD8DOxGClgoHns8YWrnhpui2ZRcW7C2"
    },
    body: JSON.stringify(data)
  });
    console.log("testing only for new fetch: iresponse3: " + JSON.stringify(response3));
      const jsonResp = await response3.json();
    response = jsonResp;
    console.log("testing only for new fetch: " + JSON.stringify(jsonResp));
    return jsonResp;
    }

const result1 =  requestFunc().then(val => {
    // got value here
    console.log("val here " + JSON.stringify(val));
    console.log("val here " + val.payment.id);
    const result = val;
    return { transaction_id: val.payment.id };
}).catch(e => {
    // error
    console.log(e);
});

    console.log("testing only for new fetch:  successfully completed ");
    console.log("testing only for new fetch:  successfully completed  response " + JSON.stringify(response));
    console.log("testing only for new fetch:  successfully completed  result1 " + JSON.stringify(result1));

    console.log("testing only for new fetch:  successfully completed before returning : " + JSON.stringify(data));
  return { transaction_id: uuidv4() };
  //return { err };
};
