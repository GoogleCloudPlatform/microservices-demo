/**
 * Using: https://github.com/njpatel/grpcc
 * src/checkoutservice $ grpcc --insecure -p proto/demo.proto -a localhost:5050 -s hipstershop.CheckoutService --exec examples/placeorder.js
 */
client.placeOrder(
  {
    user_id: '123',
    user_currency: 'USD',
    address: {
      street_address: '123 foo bar lane',
      city: 'san francisco',
      state: 'CA',
      country: 'USA',
      zip_code: 94329,
    },
    email: 'foo@bar.com',
    credit_card: {
      credit_card_number: '4009366231016609',
      credit_card_cvv: 123,
      credit_card_expiration_year: 2025,
      credit_card_expiration_month: 12,
    },
  },
  printReply
);
