#!/bin/sh


curl -X 'POST' \
  'http://rest-demo.email-service-port60000.checkout-system.skyramp.test/send-order-confirmation' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "someone@example.com",
  "order": {
    "order_id": "99ec9ebd-13fc-411d-8997-075d9a5cdb9d",
    "shipping_tracking_id": "85f19309-cdd6-4b42-abba-42f9d8d1bd60",
    "shipping_cost": {
      "currency_code": "USD",
      "units": 10,
      "nanos": 900
    },
    "shipping_address": {
      "street_address": "1600 Amp street",
      "city": "Mountain View",
      "state": "CA",
      "country": "USA",
      "zip_code": "94043"
    },
    "items": [
      {
        "item": {
          "product_id": "L9ECAV7KIM",
          "quantity": 2
        },
        "cost": {
          "currency_code": "USD",
          "units": 89,
          "nanos": 990000000
        }
      },
      {
        "item": {
          "product_id": "2ZYFJ3GM2N",
          "quantity": 1
        },
        "cost": {
          "currency_code": "USD",
          "units": 24,
          "nanos": 990000000
        }
      }
    ]
  }
}' ; echo

