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
const uuid = require('uuid/v4');
const pino = require('pino');

const { context, getSpan, setSpan, SpanKind, trace } = require('@opentelemetry/api');

const logger = pino({
  name: 'paymentservice',
  messageKey: 'message',
  changeLevelName: 'severity',
  useLevelLabels: true,
  timestamp: pino.stdTimeFunctions.unixTime,
  mixin() {
    const span = getSpan(context.active());
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

// Demo Data

// Percentage of requests to fail: [0, 1]
const API_TOKEN_FAILURE_RATE = Number.parseFloat(
  process.env['API_TOKEN_FAILURE_RATE'] || 0
);

// Percentage of requests to fail for deserialization: [0, 1]
const SERIALIZATION_FAILURE_RATE = Number.parseFloat(
  process.env['SERIALIZATION_FAILURE_RATE'] || 0
);

// Success attributes
const SUCCESS_VERSION = 'v350.9';
const SUCCESS_TENANT_LEVEL = ['gold', 'silver', 'bronze'];
const SUCCESS_K8S_POD_UID = ['payment-service-449bc'];
const API_TOKEN_SUCCESS_TOKEN = 'prod-a8cf28f9-1a1a-4994-bafa-cd4b143c3291';

// Failure attributes
const FAILURE_VERSION = 'v350.10';
const FAILURE_K8S_POD_UID = [
  'payment-service-3483d',
  'payment-service-ab82e',
  'payment-service-9aaf3',
  'payment-service-6bbaf',
];
const API_TOKEN_FAILURE_TOKEN = 'test-20e26e90-356b-432e-a2c6-956fc03f5609';

// Artificial delay
const SUCCESS_PAYMENT_SERVICE_DURATION_MILLIS = Number.parseInt(
  process.env['SUCCESS_PAYMENT_SERVICE_DURATION_MILLIS'] || 200
);
const ERROR_PAYMENT_SERVICE_DURATION_MILLIS = Number.parseInt(
  process.env['ERROR_PAYMENT_SERVICE_DURATION_MILLIS'] || 1000
);

/** Return random element from given array */
function random(arr) {
  const index = Math.floor(Math.random() * arr.length);
  return arr[index];
}

/** Returns random integer between `from` and `to` */
function randomInt(from, to) {
  return Math.floor((to - from) * Math.random() + from);
}

/**
 * Verifies the credit card number and (pretend) charges the card.
 *
 * @param {*} request
 * @return transaction_id - a random uuid v4.
 */
module.exports = async function charge(request) {
  // Get handle to the active span and some random attributes for every request. In a failure
  // case some of these might be overwritten to constrain the domain of the error.
  const grpcActiveSpan = getSpan(context.active());
  grpcActiveSpan.setAttributes({
    version: SUCCESS_VERSION,
    'tenant.level': random(SUCCESS_TENANT_LEVEL),
    kubernetes_pod_uid: random(SUCCESS_K8S_POD_UID),
  });

  // Pick successful or failing token base on configured api token failure rate
  const token =
    Math.random() < API_TOKEN_FAILURE_RATE
      ? API_TOKEN_FAILURE_TOKEN
      : API_TOKEN_SUCCESS_TOKEN;

  logger.info({ token }, 'Charging through ButtercupPayments');

  // Fail due to serialization error based on configured serialization failure rate
  if (Math.random() < SERIALIZATION_FAILURE_RATE) {
    await serializeRequestDataToProto().catch((err) => {
      const kubernetes_pod_uid = random(FAILURE_K8S_POD_UID);

      grpcActiveSpan.setAttributes({
        version: FAILURE_VERSION,
        kubernetes_pod_uid,
        error: true,
      });

      logger
        .child({
          version: FAILURE_VERSION,
          kubernetes_pod_uid,
        })
        .error(err);

      throw new InternalError('Error');
    });
  }

  // Represents an "external service call" to a payment processor. This is the "call" that will
  // either succeed or fail due to an API token issue.
  const tracer = trace.getTracer('charge')
  const externalPaymentProcessorClientSpan = tracer.startSpan(
    'buttercup.payments.api',
    {
      kind: SpanKind.CLIENT,
      attributes: {
        'peer.service': 'ButtercupPayments',
        'http.url': 'https://api.buttercup-payments.com/charge',
        'http.method': 'POST',
        'http.status_code': '200',
      },
    },
    setSpan(context.active(), grpcActiveSpan),
  );

  // Call into our "external service" for charge processing
  return buttercupPaymentsApiCharge(request, token)
    .then(({ transaction_id, cardType, cardNumber, amount }) => {
      externalPaymentProcessorClientSpan.setAttributes({
        'http.status_code': '200',
      });

      logger.info(
        {
          cardType,
          version: SUCCESS_VERSION,
          cardNumberEnding: cardNumber.substr(-4),
          'amount.currency_code': amount.currency_code,
          'amount.units': amount.units,
          'amount.nanos': amount.nanos,
        },
        'Transaction processed'
      );

      return { transaction_id };
    })
    .catch((err) => {
      externalPaymentProcessorClientSpan.setAttributes({
        'http.status_code': err.code,
      });

      if (err.code === 401) {
        // Mark error conditions on the root span; we force these for the demo
        grpcActiveSpan.setAttributes({
          version: FAILURE_VERSION,
          kubernetes_pod_uid: random(FAILURE_K8S_POD_UID),
          error: true,
        });

        // Log out error about token
        logger.error(
          {
            token: API_TOKEN_FAILURE_TOKEN,
            version: FAILURE_VERSION,
          },
          `Failed payment processing through ButtercupPayments: Invalid API Token (${API_TOKEN_FAILURE_TOKEN})`
        );
      } else {
        logger.error(`Failed payment processing through ButtercupPayments`);
      }
      throw err;
    })
    .finally(() => {
      externalPaymentProcessorClientSpan.end();
    });
};

/**
 * Attempt serialization, but it fails!
 */
async function serializeRequestDataToProto() {
  return Promise.reject(new Error('Serialization failure'));
}

/**
 * Process the charge request with the given API token. Acts as an external payment processer,
 * so the call is asynchronous and has added artificial network delay.
 *
 * @param {*} request
 * @param {*} token
 */
function buttercupPaymentsApiCharge(request, token) {
  return new Promise((resolve, reject) => {
    // Check for invalid token
    if (token === API_TOKEN_FAILURE_TOKEN) {
      const timeoutMillis = randomInt(0, ERROR_PAYMENT_SERVICE_DURATION_MILLIS);
      setTimeout(() => {
        reject(new InvalidRequestError());
      }, timeoutMillis);
      return;
    }

    // Process card
    const { amount, credit_card: creditCard } = request;
    const cardNumber = creditCard.credit_card_number;
    const cardInfo = cardValidator(cardNumber);
    const { card_type: cardType, valid } = cardInfo.getCardDetails();

    if (!valid) {
      throw new InvalidCreditCard();
    }

    // Only VISA and mastercard is accepted, other card types (AMEX, dinersclub) will
    // throw UnacceptedCreditCard error.
    if (!(cardType === 'visa' || cardType === 'mastercard')) {
      throw new UnacceptedCreditCard(cardType);
    }

    // Also validate expiration is > today.
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();
    const {
      credit_card_expiration_year: year,
      credit_card_expiration_month: month,
    } = creditCard;
    if (currentYear * 12 + currentMonth > year * 12 + month) {
      throw new ExpiredCreditCard(cardNumber.replace('-', ''), month, year);
    }

    const timeoutMillis = randomInt(0, SUCCESS_PAYMENT_SERVICE_DURATION_MILLIS);
    setTimeout(() => {
      resolve({ transaction_id: uuid(), cardType, cardNumber, amount });
    }, timeoutMillis);
  });
}

// Error Types

class InternalError extends Error {
  constructor(message) {
    super(message);
    this.code = 500;
  }
}

class InvalidRequestError extends Error {
  constructor(token) {
    super('Invalid request');
    this.code = 401; // Authorization error
  }
}

class CreditCardError extends Error {
  constructor(message) {
    super(message);
    this.code = 400; // Invalid argument error
  }
}

class InvalidCreditCard extends CreditCardError {
  constructor(cardType) {
    super(`Credit card info is invalid`);
  }
}

class UnacceptedCreditCard extends CreditCardError {
  constructor(cardType) {
    super(
      `Sorry, we cannot process ${cardType} credit cards. Only VISA or MasterCard is accepted.`
    );
  }
}

class ExpiredCreditCard extends CreditCardError {
  constructor(number, month, year) {
    super(
      `Your credit card (ending ${number.substr(
        -4
      )}) expired on ${month}/${year}`
    );
  }
}
