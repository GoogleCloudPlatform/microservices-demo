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
import os
import requests
import json
from locust import FastHttpUser, TaskSet, between
from faker import Faker
import datetime
fake = Faker()

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

# Sample data for multicloud load testing
TRANSACTION_ITEMS = [
    "Office Supplies", "Software License", "Server Hardware", "Marketing Campaign",
    "Consulting Services", "Cloud Infrastructure", "Development Tools", "Training Materials"
]

TRANSACTION_TYPES = [
    "user_login", "checkout", "payment_processing", "data_sync", "report_generation",
    "file_upload", "search_query", "api_call"
]

CUSTOMER_NAMES = [
    ("John", "Doe"), ("Jane", "Smith"), ("Alice", "Johnson"), ("Bob", "Williams"),
    ("Carol", "Brown"), ("David", "Davis"), ("Eva", "Miller"), ("Frank", "Wilson")
]

# Configuration from environment variables
AWS_ACCOUNTING_URL = os.getenv('AWS_ACCOUNTING_URL', '')
AZURE_ANALYTICS_URL = os.getenv('AZURE_ANALYTICS_URL', '')
GCP_CRM_URL = os.getenv('GCP_CRM_URL', '')
GCP_INVENTORY_URL = os.getenv('GCP_INVENTORY_URL', '')

def index(l):
    l.client.get("/")

def setCurrency(l):
    currencies = ['EUR', 'USD', 'JPY', 'CAD', 'GBP', 'TRY']
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
        'quantity': random.randint(1,10)})
    
def empty_cart(l):
    l.client.post('/cart/empty')

def checkout(l):
    addToCart(l)
    current_year = datetime.datetime.now().year+1
    l.client.post("/cart/checkout", {
        'email': fake.email(),
        'street_address': fake.street_address(),
        'zip_code': fake.zipcode(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'country': fake.country(),
        'credit_card_number': fake.credit_card_number(card_type="visa"),
        'credit_card_expiration_month': random.randint(1, 12),
        'credit_card_expiration_year': random.randint(current_year, current_year + 70),
        'credit_card_cvv': f"{random.randint(100, 999)}",
    })
    
def logout(l):
    l.client.get('/logout')

# New multicloud service tasks
def processTransaction(l):
    """Process transaction via AWS Accounting Service: POST transaction then GET all transactions"""
    if not AWS_ACCOUNTING_URL:
        return
    
    try:
        # Generate sample transaction data
        transaction_data = {
            "item": random.choice(TRANSACTION_ITEMS),
            "price": round(random.uniform(10.0, 999.99), 2),
            "date": fake.date_between(start_date='-30d', end_date='today').strftime('%Y-%m-%d')
        }
        
        # POST new transaction
        response = requests.post(
            f"{AWS_ACCOUNTING_URL}/transactions",
            json=transaction_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # GET all transactions
        requests.get(f"{AWS_ACCOUNTING_URL}/transactions", timeout=10)
        
    except Exception as e:
        print(f"AWS Accounting Service error: {e}")

def recordMetrics(l):
    """Record performance metrics via Azure Analytics Service: POST metric then GET all metrics"""
    if not AZURE_ANALYTICS_URL:
        return
    
    try:
        # Generate sample metric data
        metric_data = {
            "transactionType": random.choice(TRANSACTION_TYPES),
            "durationMs": random.randint(50, 5000),
            "success": random.choice([True, False])
        }
        
        # POST new metric
        response = requests.post(
            f"{AZURE_ANALYTICS_URL}/metrics",
            json=metric_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # GET all metrics
        requests.get(f"{AZURE_ANALYTICS_URL}/metrics", timeout=10)
        
    except Exception as e:
        print(f"Azure Analytics Service error: {e}")

def manageCustomer(l):
    """Manage customer via GCP CRM Service: POST customer then GET all customers"""
    if not GCP_CRM_URL:
        return
    
    try:
        # Generate sample customer data
        name, surname = random.choice(CUSTOMER_NAMES)
        customer_data = {
            "name": name,
            "surname": surname
        }
        
        # POST new customer
        response = requests.post(
            f"{GCP_CRM_URL}/customers",
            json=customer_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # GET all customers
        requests.get(f"{GCP_CRM_URL}/customers", timeout=10)
        
    except Exception as e:
        print(f"GCP CRM Service error: {e}")

def checkInventory(l):
    """Check inventory via GCP Inventory Service (PSC): GET inventory and specific products"""
    if not GCP_INVENTORY_URL:
        return
    
    try:
        # GET all inventory
        requests.get(f"{GCP_INVENTORY_URL}/inventory", timeout=10)
        
        # GET specific product inventory (random product from our catalog)
        product_id = random.choice(products)
        requests.get(f"{GCP_INVENTORY_URL}/inventory/{product_id}", timeout=10)
        
        # Occasionally simulate inventory operations
        if random.random() < 0.3:  # 30% chance
            # Reserve stock for a product
            reserve_data = {"quantity": random.randint(1, 3)}
            requests.post(
                f"{GCP_INVENTORY_URL}/inventory/{product_id}/reserve",
                json=reserve_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        
    except Exception as e:
        print(f"GCP Inventory Service (PSC) error: {e}")

class UserBehavior(TaskSet):

    def on_start(self):
        index(self)

    tasks = {
        index: 1,
        setCurrency: 2,
        browseProduct: 10,
        addToCart: 2,
        viewCart: 3,
        checkout: 1,
        processTransaction: 3,
        recordMetrics: 3,
        manageCustomer: 3,
        checkInventory: 4
    }

class WebsiteUser(FastHttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 10)
