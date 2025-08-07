import cardValidator from 'simple-card-validator';
import { v4 as uuidv4 } from 'uuid';
import pino from 'pino';

const logger = pino({
  name: 'paymentservice-charge',
  messageKey: 'message',
  formatters: {
    level (logLevelString, logLevelNum) {
      return { severity: logLevelString }
    }
  }
});

export class CreditCardError extends Error {
  public code: number;
  constructor (message: string) {
    super(message);
    this.code = 400; // Invalid argument error
  }
}

export class InvalidCreditCard extends CreditCardError {
  constructor () {
    super('Credit card info is invalid');
  }
}

export class UnacceptedCreditCard extends CreditCardError {
  constructor (cardType: string) {
    super(`Sorry, we cannot process ${cardType} credit cards. Only VISA or MasterCard is accepted.`);
  }
}

export class ExpiredCreditCard extends CreditCardError {
  constructor (number: string, month: number, year: number) {
    super(`Your credit card (ending ${number.substr(-4)}) expired on ${month}/${year}`);
  }
}

interface CreditCard {
    credit_card_number: string;
    credit_card_expiration_year: number;
    credit_card_expiration_month: number;
}

interface ChargeRequest {
    amount: any;
    credit_card: CreditCard
}

export function charge(request: ChargeRequest): { transaction_id: string } {
  const { amount, credit_card: creditCard } = request;
  const cardNumber = creditCard.credit_card_number;
  const cardInfo = cardValidator(cardNumber);
  const {
    card_type: cardType,
    valid
  } = cardInfo.getCardDetails();

  if (!valid) { throw new InvalidCreditCard(); }

  if (!(cardType === 'visa' || cardType === 'mastercard')) { throw new UnacceptedCreditCard(cardType as string); }

  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();
  const { credit_card_expiration_year: year, credit_card_expiration_month: month } = creditCard;
  if ((currentYear * 12 + currentMonth) > (year * 12 + month)) { throw new ExpiredCreditCard(cardNumber.replace(/-/g, ''), month, year); }

  logger.info(`Transaction processed: ${cardType} ending ${cardNumber.substr(-4)} \
    Amount: ${amount.currency_code}${amount.units}.${amount.nanos}`);

  return { transaction_id: uuidv4() };
};
