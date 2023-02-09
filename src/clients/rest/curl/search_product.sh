#!/bin/sh

set -e

curl -X 'GET' \
  'http://productcatalogservice:60000/search-products?query=kitchen' \
  -H 'accept: application/json' ; echo
