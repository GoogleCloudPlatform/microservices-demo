const chai = require('chai');
const axios = require('axios');
const { expect } = chai;

const BASE_URL = process.env.machine_dns || 'http://10.2.10.163:8081';

describe('Api Tests', function () {
  let session;

  before(function () {
    session = axios.create({ baseURL: BASE_URL });
  });

  this.timeout(10000);  // Increase the timeout for slow tests

  it('should return 200 for index page', async function () {
    const response = await session.get('/');
    expect(response.status).to.equal(200);
  });

  it('should be able to set different currencies', async function () {
    const currencies = ['EUR', 'USD', 'JPY', 'CAD'];
    for (const currency of currencies) {
      const response = await session.post('/setCurrency', { currency_code: currency });
      expect(response.status).to.equal(200);
    }
  });

  it('should return 200 for browsing products', async function () {
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
      const response = await session.get(`/product/${product_id}`);
      expect(response.status).to.equal(200);
    }
  });

  it('should return 404 for a non-existent route', async function () {
    try {
      await session.get('/nonexistent-route');
    } catch (error) {
      expect(error.response.status).to.equal(404);
    }
  });

  it('should return 400 for invalid request data', async function () {
    try {
      await session.post('/setCurrency', { invalid_key: 'invalid_value' });
    } catch (error) {
      expect(error.response.status).to.equal(400);
    }
  });
});
