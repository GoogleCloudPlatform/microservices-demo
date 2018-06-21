const cardValidator = require('simple-card-validator');
const uuid = require('uuid/v4');

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
    super(`Sorry, we cannot process ${cardType} credit cards. Only VISA or MasterCard is accepted.`);
  }
}

class ExpiredCreditCard extends CreditCardError {
  constructor(number, month, year) {
    super(`Your credit card (ending ${number.substr(-4)}) expired on ${month}/${year}`);
  }
}

/**
 * Verifies the credit card number and (pretend) charges the card.
 *
 * @param {*} request
 * @return transaction_id - a random uuid v4.
 */
module.exports = function charge(request) {
  const { amount, credit_card: creditCard } = request;
  const cardNumber = creditCard.credit_card_number;
  const cardInfo = cardValidator(cardNumber);
  const {
    card_type: cardType,
    valid,
    cvv_length: cvvLength,
  } = cardInfo.getCardDetails();

  if (!valid)
    throw new InvalidCreditCard();

  // Only VISA and mastercard is accepted, other card types (AMEX, dinersclub) will
  // throw UnacceptedCreditCard error.
  if (!(cardType === 'visa' || cardType == 'mastercard'))
    throw new UnacceptedCreditCard(cardType);

  // Also validate expiration is > today.
  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();
  const { credit_card_expiration_year: year, credit_card_expiration_month: month } = creditCard;
  if ((currentYear * 12 + currentMonth) > (year * 12 + month))
    throw new ExpiredCreditCard(cardNumber.replace('-', ''), month, year);

  console.log(`Transaction processed: ${cardType} ending ${cardNumber.substr(-4)} \
    Amount: ${amount.currency_code}${amount.amount.decimal}.${amount.amount.fractional}`)

  return { transaction_id: uuid() }
}

