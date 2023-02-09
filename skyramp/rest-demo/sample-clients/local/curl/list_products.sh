#!/bin/sh

set -e

curl -X 'GET' \
  'http://rest-demo.product-catalog-service-port60000.checkout-system.skyramp.test/get-products' \
  -H 'accept: application/json' ; echo
