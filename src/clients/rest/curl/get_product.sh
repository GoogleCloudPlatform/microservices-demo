#1/bin/sh


set -e

curl -X 'GET' \
  'http://productcatalogservice:60000/get-product?product_id=OLJCESPC7Z' \
  -H 'accept: application/json' ; echo
