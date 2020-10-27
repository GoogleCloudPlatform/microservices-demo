#!/usr/bin/env python

# Copyright 2020 Google Inc. All rights reserved.
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
from locust import task, HttpUser, TaskSet

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

currencies = [
    'EUR',
    'USD',
    'JPY',
    'GBP',
    'TRY',
    'CAD']

# Define specific frontend actions.

@task
def index(l):
    l.client.get("/")

@task
def setCurrency(l):
    l.client.post("/setCurrency",
        {'currency_code': random.choice(currencies)})

@task
def browseProduct(l):
    l.client.get("/product/" + random.choice(products))

@task
def viewCart(l):
    l.client.get("/cart")

@task
def emptyCart(l):
    l.client.post("/cart/empty")

@task
def addToCart(l):
    product = random.choice(products)
    l.client.get("/product/" + product)
    l.client.post("/cart", {
        'product_id': product,
        'quantity': random.choice([1,2,3,4,5,10])})

@task
def checkout(l):
    addToCart(l)
    l.client.post("/cart/checkout", {
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

# LocustIO TaskSet classes defining detailed user behaviors.

class PurchasingBehavior(TaskSet):

    def on_start(self):
        index(self)

    tasks = {index: 1,
        setCurrency: 1,
        browseProduct: 2,
        addToCart: 2,
        viewCart: 1,
        checkout: 1}

class WishlistBehavior(TaskSet):

    def on_start(self):
        index(self)

    tasks = {index: 1,
        setCurrency: 1,
        browseProduct: 5,
        addToCart: 10,
        viewCart: 5,
        emptyCart: 2}

class BrowsingBehavior(TaskSet):

    def on_start(self):
        index(self)

    tasks = {index: 5,
        setCurrency: 1,
        browseProduct: 10}

# LocustIO Locust classes defining general user scenarios.

class PurchasingUser(HttpUser):
    '''
    User that browses products, adds to cart, and purchases via checkout.
    '''
    tasks = [PurchasingBehavior]
    min_wait = 1000
    max_wait = 10000

class WishlistUser(HttpUser):
    '''
    User that browses products, adds to cart, empties cart, but never purchases.
    '''
    tasks = [WishlistBehavior]
    min_wait = 1000
    max_wait = 10000

class BrowsingUser(HttpUser):
    '''
    User that only browses products.
    '''
    tasks = [BrowsingBehavior]
    min_wait = 1000
    max_wait = 10000
