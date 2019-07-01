#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random

import requests
import sys

BASE = sys.argv[1]

products = [
    '0PUK6V6EV0',
    '1YMWWN1N4O',
    '2ZYFJ3GM2N',
    '66VCHSJNUP',
    '6E92ZMYYFZ',
    '9SIQT8TOJO',
    'L9ECAV7KIM',
    'LS4PSXUNUM',
    'OLJCESPC7Z']


def index():
  requests.get(BASE + "/")


def setCurrency():
  currencies = ['EUR', 'USD', 'JPY', 'CAD']
  requests.post(BASE + "/setCurrency",
                {'currency_code': random.choice(currencies)})


def browseProduct():
  requests.get(BASE + "/product/" + random.choice(products))


def viewCart():
  requests.get(BASE + "/cart")


def addToCart():
  product = random.choice(products)
  requests.get(BASE + "/product/" + product)
  requests.post(BASE + "/cart", {
      'product_id': product,
      'quantity': random.choice([1, 2, 3, 4, 5, 10])})


def checkout():
  addToCart()
  requests.post(BASE + "/cart/checkout", {
      'email': 'someone@example.com',
      'street_address': '1600 Amphitheatre Parkway',
      'zip_code': '94043',
      'city': 'Mountain View',
      'state': 'CA',
      'country': 'United States',
      'credit_card_number': '4432-8015-6152-0454',
      'credit_card_expiration_month': '1',
      'credit_card_expiration_year': '2039',
      'credit_card_cvv': '672',
  })


if not BASE:
  print("ERROR: no frontend address")
else:
  print("pinging" + BASE)
index()
browseProduct()
addToCart()
viewCart()
checkout()
print("pinging complete")
