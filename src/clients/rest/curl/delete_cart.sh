#!/bin/sh

set -e

curl -X 'DELETE' \
  'http://cartservice:60000/cart/user_id/abcde' \
   -H 'accept: application/json' ; echo
