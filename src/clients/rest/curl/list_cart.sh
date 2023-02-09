#!/bin/sh

set -e

curl -X 'GET' \
  'http://cartservice:60000/cart/user_id/abcde' \
   -H 'accept: application/json' ; echo
