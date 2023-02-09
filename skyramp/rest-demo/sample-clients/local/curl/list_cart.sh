#!/bin/sh

set -e

curl -X 'GET' \
  'http://rest-demo.cart-service-port60000.checkout-system.skyramp.test/cart/user_id/abcde' \
   -H 'accept: application/json' ; echo
