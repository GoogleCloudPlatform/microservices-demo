import random
import requests
import pytest
import os
import threading

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

load = 10  # number of users for load test

BASE_URL = os.environ.get("machine_dns", "10.2.10.163:8081")  # internal or external test

def test_load():
    threads = []
    for _ in range(load):
        thread = threading.Thread(target=test_session)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def test_session():
    order = [test_index, test_set_currency, test_browse_product, test_add_to_cart, test_view_cart, test_add_to_cart,
             test_checkout]
    session = requests.Session()
    for o in order:
        o(session)
        # print("hello")


def test_bad_requests(r=requests):
    response = r.get(BASE_URL + "/product/89")
    assert response.status_code == 500
    r.post(BASE_URL + "/setCurrency", data={'currency_code': 'not a currency'})
    assert response.status_code == 500


def test_index(r=requests):
    response = r.get(BASE_URL + "/")
    assert response.status_code == 200


def test_set_currency(r=requests):
    for currency in ['EUR', 'USD', 'JPY', 'CAD']:
        data = {'currency_code': currency}
        response = r.post(BASE_URL + "/setCurrency", data=data)
        assert response.status_code == 200
    r.post(BASE_URL + "/setCurrency", data={'currency_code': random.choice(['EUR', 'USD', 'JPY', 'CAD'])})


def test_browse_product(r=requests):
    for product_id in products:
        response = r.get(BASE_URL + "/product/" + product_id)
        assert response.status_code == 200


def test_view_cart(r=requests):
    response = r.get(BASE_URL + "/cart")
    assert response.status_code == 200
    response = r.post(BASE_URL + "/cart/empty")
    assert response.status_code == 200


def test_add_to_cart(r=requests):
    for product_id in products:
        response = r.get(BASE_URL + "/product/" + product_id)
        assert response.status_code == 200

        data = {
            'product_id': product_id,
            'quantity': random.choice([1, 2, 3, 4, 5, 10])
        }
        response = requests.post(BASE_URL + "/cart", data=data)
        assert response.status_code == 200


def test_icon(r=requests):
    response = r.get(BASE_URL + "/static/favicon.ico")
    assert response.status_code == 200
    response = r.get(BASE_URL + "/static/img/products/hairdryer.jpg")
    assert response.status_code == 200


def test_checkout(r=requests):
    assert len(products) == 9
    for product_id in products:
        data = {
            'product_id': product_id,
            'quantity': random.choice([1, 2, 3, 4, 5, 10]),
            'email': 'someone@example.com',
            'street_address': '1600 Amphitheatre Parkway',
            'zip_code': '94043',
            'city': 'Mountain View',
            'state': 'CA',
            'country': 'United States',
            'credit_card_number': '4432-8015-6152-0454',
            'credit_card_expiration_month': '1',
            'credit_card_expiration_year': '2039',
            'credit_card_cvv': '672'
        }
        response = r.post(BASE_URL + "/cart/checkout", data=data)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main()
