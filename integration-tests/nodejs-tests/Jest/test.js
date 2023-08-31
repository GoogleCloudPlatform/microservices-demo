const axios = require('axios');

const BASE_URL = process.env.machine_dns || 'http://10.2.10.163:8081';

describe('Api Tests', () => {
  let session;

  beforeAll(() => {
    session = axios.create({ baseURL: BASE_URL });
  });

  it('should return 200 for index page', async () => {
    const response = await session.get('/');
    expect(response.status).toBe(200);
  });

  it('should be able to set different currencies', async () => {
    const currencies = ['EUR', 'USD', 'JPY', 'CAD'];
    for (const currency of currencies) {
      const response = await session.post('/setCurrency', { currency_code: currency });
      expect(response.status).toBe(200);
    }
  });

  it('should return 200 for browsing products', async () => {
    const products = [
      '0PUK6V6EV0',
      '1YMWWN1N4O',
      // ... other product IDs
    ];

    for (const product_id of products) {
      const response = await session.get(`/product/${product_id}`);
      expect(response.status).toBe(200);
    }
  });

  it('should return 404 for a non-existent route', async () => {
    try {
      await session.get('/nonexistent-route');
    } catch (error) {
      expect(error.response.status).toBe(404);
    }
  });

  it('should return 400 for invalid request data', async () => {
    try {
      await session.post('/setCurrency', { invalid_key: 'invalid_value' });
    } catch (error) {
      expect(error.response.status).toBe(400);
    }
  });
});
