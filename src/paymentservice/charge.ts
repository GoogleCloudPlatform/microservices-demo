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

import cardValidator from 'simple-card-validator';
import { v4 as uuidv4 } from 'uuid';
import pino from 'pino';

const logger = pino({
  name: 'paymentservice-charge',
  messageKey: 'message',
  formatters: {
    level(logLevelString: string, logLevelNum: number): object {
      return { severity: logLevelString };
    },
  },
});

interface Money {
  currency_code: string;
  units: number;
  nanos: number;
}

interface CreditCardInfo {
  credit_card_number: string;
  credit_card_cvv: number;
  credit_card_expiration_year: number;
  credit_card_expiration_month: number;
}

interface ChargeRequest {
  amount: Money;
  credit_card: CreditCardInfo;
}

interface ChargeResponse {
  transaction_id: string;
}

class CreditCardError extends Error {
  public code: number;
  constructor(message: string) {
    super(message);
    this.code = 400; // Invalid argument error
  }
}

class InvalidCreditCard extends CreditCardError {
  constructor() {
    super('Credit card info is invalid');
  }
}

class UnacceptedCreditCard extends CreditCardError {
  constructor(cardType?: string) {
    super(`Sorry, we cannot process ${cardType || 'provided'} credit cards. Only VISA or MasterCard is accepted.`);
  }
}

class ExpiredCreditCard extends CreditCardError {
  constructor(number: string, month: number, year: number) {
    super(`Your credit card (ending ${number.substr(-4)}) expired on ${month}/${year}`);
  }
}

/**
 * Verifies the credit card number and (pretend) charges the card.
 *
 * @param {ChargeRequest} request
 * @return {ChargeResponse} transaction_id - a random uuid.
 */
export default function charge(request: ChargeRequest): ChargeResponse {
  const { amount, credit_card: creditCard } = request;
  const cardNumber = creditCard.credit_card_number;
  const cardInfo = cardValidator(cardNumber);
  // cardInfo.getCardDetails() is not well-typed in @types/simple-card-validator, so using 'any'
  const {
    card_type: cardType,
    valid,
  }: any = cardInfo.getCardDetails();

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
  const { credit_card_expiration_year: year, credit_card_expiration_month: month } = creditCard;
  if (year < currentYear || (year === currentYear && month < currentMonth)) {
    throw new ExpiredCreditCard(cardNumber.replace(/-/g, ''), month, year);
  }

  logger.info(`Transaction processed: ${cardType} ending ${cardNumber.substr(-4)} \
    Amount: ${amount.currency_code}${amount.units}.${amount.nanos}`);

  return { transaction_id: uuidv4() };
}
