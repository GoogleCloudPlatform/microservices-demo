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

import math
import random
import time
from locust import HttpLocust, TaskSet

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


def index(l):
    l.client.get("/")


def setCurrency(l):
    currencies = ['EUR', 'USD', 'JPY', 'CAD']
    l.client.post("/setCurrency",
                  {'currency_code': random.choice(currencies)})


def browseProduct(l):
    l.client.get("/product/" + random.choice(products))


def viewCart(l):
    l.client.get("/cart")


def addToCart(l):
    product = random.choice(products)
    l.client.get("/product/" + product)
    l.client.post("/cart", {
        'product_id': product,
        'quantity': random.choice([1, 2, 3, 4, 5, 10])})


def checkout(l):
    addToCart(l)
    # For five minutes every other hour, credit cards passed by the user will be
    # invalid and the paymentservice will fail.
    now = time.localtime()
    expiration_year = '2015' if (now.tm_hour % 2) & (now.tm_min < 5) else '2060'
    l.client.post("/cart/checkout", {
        'email': 'someone@example.com',
        'street_address': '1600 Amphitheatre Parkway',
        'zip_code': '94043',
        'city': 'Mountain View',
        'state': 'CA',
        'country': 'United States',
        'credit_card_number': '4432-8015-6152-0454',
        'credit_card_expiration_month': '1',
        'credit_card_expiration_year': expiration_year,
        'credit_card_cvv': '672',
    })


class UserBehavior(TaskSet):
    min_wait = 500
    max_wait = 15000

    tasks = {index: 1,
             setCurrency: 2,
             browseProduct: 10,
             addToCart: 2,
             viewCart: 3,
             checkout: 1}

    def on_start(self):
        index(self)

    def wait_function(self):
        """Wait time between user activity is diurnal.

        Compute user's activity rate (wait time between actions) so traffic is
        minimum at hrs=0.0|24.0 and maximum at hrs=12.0.
        """
        now = time.localtime()
        hrs = now.tm_hour + now.tm_min/60.0
        # Compute scale factor is between 0 and 1.
        traffic_scaler = -1.0 * math.cos(2.0 * math.pi * hrs / 24)
        traffic_scaler = (traffic_scaler + 1) / 2.0

        # Scale traffic between minimum and maximum wait times.
        wait = self.max_wait + (self.min_wait - self.max_wait) * traffic_scaler
        return round(wait)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
