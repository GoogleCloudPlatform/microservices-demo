/**
 * Using: https://github.com/njpatel/grpcc
 * src/checkoutservice $ grpcc --insecure -p proto/demo.proto -a localhost:3002 -s hipstershop.PaymentService --exec examples/charge.js
 */
client.charge(
  {
    amount: {
      currency_code: 'USD',
      units: 1,
      nanos: 0,
    },
    credit_card: {
      credit_card_number: '4009366231016609',
      credit_card_cvv: 123,
      credit_card_expiration_year: 2025,
      credit_card_expiration_month: 12,
    },
  },
  printReply
);
