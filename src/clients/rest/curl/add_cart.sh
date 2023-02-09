#!/bin/sh

set -e

curl -X 'POST' 'http://cartservice:60000/cart/user_id/abcde' \
  -H 'accept: application/json' \
  -H 'content-type: application/json' \
  -d '{
  "product_id": "L9ECAV7KIM",
  "quantity": 1 
}'; echo

