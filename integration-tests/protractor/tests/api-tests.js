// api-tests.js

const { browser, by, element } = require('protractor');
const chai = require('chai');
const { expect } = chai;

describe('API Tests', function () {
  // Set the base URL for your application.
  const BASE_URL = process.env.machine_dns || 'http://10.2.10.163:8081';

  before(function () {
    // Before all tests, navigate to the base URL.
    browser.get(BASE_URL);
  });

  it('should return 200 for index page', async function () {
    // Navigate to the root URL and verify the status code.
    const statusCode = await browser.executeAsyncScript(function(callback) {
      fetch('/').then(function(response) {
        callback(response.status);
      });
    });
    expect(statusCode).to.equal(200);
  });

  it('should be able to set different currencies', async function () {
    // List of currencies to test.
    const currencies = ['EUR', 'USD', 'JPY', 'CAD'];

    for (const currency of currencies) {
      // Send a POST request to setCurrency and verify the status code.
      const statusCode = await browser.executeAsyncScript(function(currency, callback) {
        fetch('/setCurrency', {
          method: 'POST',
          body: JSON.stringify({ currency_code: currency }),
          headers: { 'Content-Type': 'application/json' }
        }).then(function(response) {
          callback(response.status);
        });
      }, currency);
      expect(statusCode).to.equal(200);
    }
  });

  it('should return 200 for browsing products', async function () {
    // List of product IDs to test.
    const products = [
      '0PUK6V6EV0',
      '1YMWWN1N4O',
      '2ZYFJ3GM2N',
      '66VCHSJNUP',
      '6E92ZMYYFZ',
      '9SIQT8TOJO',
      'L9ECAV7KIM',
      'LS4PSXUNUM',
      'OLJCESPC7Z'
    ];

    for (const product_id of products) {
      // Send a GET request to /product/{product_id} and verify the status code.
      const statusCode = await browser.executeAsyncScript(function(product_id, callback) {
        fetch('/product/' + product_id).then(function(response) {
          callback(response.status);
        });
      }, product_id);
      expect(statusCode).to.equal(200);
    }
  });

  it('should return 404 for a non-existent route', async function () {
    // Send a GET request to a non-existent route and expect a 404 status code.
    const statusCode = await browser.executeAsyncScript(function(callback) {
      fetch('/nonexistent-route').then(function(response) {
        callback(response.status);
      }).catch(function(error) {
        // Catch any errors, e.g., network failures, and handle them as well.
        if (error.response) {
          callback(error.response.status);
        } else {
          callback(500); // Handle other errors as 500 Internal Server Error.
        }
      });
    });
    expect(statusCode).to.equal(404);
  });

  it('should return 400 for invalid request data', async function () {
    // Send a POST request with invalid data and expect a 400 status code.
    const statusCode = await browser.executeAsyncScript(function(callback) {
      fetch('/setCurrency', {
        method: 'POST',
        body: JSON.stringify({ invalid_key: 'invalid_value' }),
        headers: { 'Content-Type': 'application/json' }
      }).then(function(response) {
        callback(response.status);
      }).catch(function(error) {
        if (error.response) {
          callback(error.response.status);
        } else {
          callback(500);
        }
      });
    });
    expect(statusCode).to.equal(400);
  });
});
