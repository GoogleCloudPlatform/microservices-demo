#!/bin/sh

set -e

curl -X 'GET' \
  'http://productcatalogservice:60000/get-products' \
  -H 'accept: application/json' ; echo
