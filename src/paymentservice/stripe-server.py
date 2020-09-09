#! /usr/bin/env python3.6

"""
server.py
Stripe Recipe.
Python 3.6 or newer required.
"""

import stripe
import json
import os

from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv, find_dotenv

# Setup Stripe python client library
load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

static_dir = str(os.path.abspath(os.path.join(
    __file__, "..", os.getenv("STATIC_DIR"))))
app = Flask(__name__, static_folder=static_dir,
            static_url_path="", template_folder=static_dir)


@app.route('/', methods=['GET'])
def get_example():
    return render_template('index.html')


@app.route('/publishable-key', methods=['GET'])
def get_publishable_key():
    return jsonify({'publishableKey': os.getenv('STRIPE_PUBLISHABLE_KEY')})

# Fetch the Checkout Session to display the JSON result on the success page
@app.route('/checkout-session', methods=['GET'])
def get_checkout_session():
    id = request.args.get('sessionId')
    checkout_session = stripe.checkout.Session.retrieve(id)
    return jsonify(checkout_session)


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = json.loads(request.data)
    domain_url = os.getenv('DOMAIN')
    price_id = os.getenv('SUBSCRIPTION_PRICE_ID')
    product_id = os.getenv('DONATION_PRODUCT_ID')
    line_items = [{"price": price_id, "quantity": 1}]

    try:
        if data['donation'] > 0:
            line_items.append(
                {"quantity": 1, "price_data": {"product": product_id, "unit_amount": data['donation'], "currency": "usd"}})
        # Sign customer up for subscription
        checkout_session = stripe.checkout.Session.create(
            mode="subscription",
            success_url=domain_url +
            "/success.html?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "/cancel.html",
            payment_method_types=["card"],
            line_items=line_items
        )

        return jsonify({'checkoutSessionId': checkout_session['id']})
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/webhook', methods=['POST'])
def webhook_received():
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    if event_type == 'checkout.session.completed':
        items = data_object['display_items']
        customer = stripe.Customer.retrieve(data_object['customer'])

        if len(items) > 0 and items[0].custom and items[0].custom.name == 'Pasha e-book':
            print(
                '🔔 Customer is subscribed and bought an e-book! Send the e-book to ' + customer.email)
        else:
            print(
                '🔔 Customer is subscribed but did not buy an e-book')

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(port=4242)
