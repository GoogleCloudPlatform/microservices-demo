const axios = require('axios');
const { expect } = require('chai');

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

const load = 10; // number of users for load test

const BASE_URL = `http://${process.env.FRONTEND_ADDR || '10.2.10.105:8080'}`;

describe('API Tests', () => {
  it('should perform load test', async () => {
    const promises = [];
    for (let i = 0; i < load; i++) {
      promises.push(testSession());
    }
    await Promise.all(promises);
  });

  it('should handle bad requests', async () => {
    try {
      const response = await axios.get(`${BASE_URL}/product/89`);
      expect(response.status).to.equal(500);

      const badRequestResponse = await axios.post(`${BASE_URL}/setCurrency`, {
        currency_code: 'not a currency'
      });
      expect(badRequestResponse.status).to.equal(500);
    } catch (error) {
      throw error;
    }
  });

  it('should browse products', async () => {
    try {
      for (const product_id of products) {
        const response = await axios.get(`${BASE_URL}/product/${product_id}`);
        expect(response.status).to.equal(200);
      }
    } catch (error) {
      throw error;
    }
  });

  it('should view cart', async () => {
    try {
      const response = await axios.get(`${BASE_URL}/cart`);
      expect(response.status).to.equal(200);

      const emptyCartResponse = await axios.post(`${BASE_URL}/cart/empty`);
      expect(emptyCartResponse.status).to.equal(200);
    } catch (error) {
      throw error;
    }
  });

  it('should add to cart', async () => {
    try {
      for (const product_id of products) {
        const response = await axios.get(`${BASE_URL}/product/${product_id}`);
        expect(response.status).to.equal(200);

        const data = {
          product_id,
          quantity: getRandomQuantity()
        };
        const addToCartResponse = await axios.post(`${BASE_URL}/cart`, data);
        expect(addToCartResponse.status).to.equal(200);
      }
    } catch (error) {
      throw error;
    }
  });

  it('should view icon', async () => {
    try {
      const iconResponse = await axios.get(`${BASE_URL}/static/favicon.ico`);
      expect(iconResponse.status).to.equal(200);

      const imageResponse = await axios.get(`${BASE_URL}/static/img/products/hairdryer.jpg`);
      expect(imageResponse.status).to.equal(200);
    } catch (error) {
      throw error;
    }
  });

  it('should perform checkout', async () => {
    try {
      for (const product_id of products) {
        const data = {
          product_id,
          quantity: getRandomQuantity(),
          email: 'someone@example.com',
          street_address: '1600 Amphitheatre Parkway',
          zip_code: '94043',
          city: 'Mountain View',
          state: 'CA',
          country: 'United States',
          credit_card_number: '4432-8015-6152-0454',
          credit_card_expiration_month: '1',
          credit_card_expiration_year: '2039',
          credit_card_cvv: '672'
        };
        const checkoutResponse = await axios.post(`${BASE_URL}/cart/checkout`, data);
        expect(checkoutResponse.status).to.equal(200);
      }
    } catch (error) {
      throw error;
    }
  });
});

function getRandomQuantity() {
  return Math.floor(Math.random() * 5) + 1;
}

async function testSession() {
  const order = [
    testIndex,
    testSetCurrency,
    testBrowseProduct,
    testAddToCart,
    testViewCart,
    testAddToCart,
    testCheckout
  ];
  const session = axios.create();
  for (const o of order) {
    await o(session);
  }
}

async function testIndex(session) {
  const response = await session.get(`${BASE_URL}/`);
  expect(response.status).to.equal(200);
}

async function testSetCurrency(session) {
  try {
    const currencies = ['EUR', 'USD', 'JPY', 'CAD'];
    for (const currency of currencies) {
      const response = await session.post(`${BASE_URL}/setCurrency`, {
        currency_code: currency
      });
      expect(response.status).to.equal(200);
    }

    const randomCurrencyResponse = await session.post(`${BASE_URL}/setCurrency`, {
      currency_code: currencies[Math.floor(Math.random() * currencies.length)]
    });
    expect(randomCurrencyResponse.status).to.equal(200);
  } catch (error) {
    throw error;
  }
}

async function testBrowseProduct(session) {
  try {
    for (const product_id of products) {
      const response = await session.get(`${BASE_URL}/product/${product_id}`);
      expect(response.status).to.equal(200);
    }
  } catch (error) {
    throw error;
  }
}

async function testViewCart(session) {
  try {
    const response = await session.get(`${BASE_URL}/cart`);
    expect(response.status).to.equal(200);

    const emptyCartResponse = await session.post(`${BASE_URL}/cart/empty`);
    expect(emptyCartResponse.status).to.equal(200);
  } catch (error) {
    throw error;
  }
}

async function testAddToCart(session) {
  try {
    for (const product_id of products) {
      const response = await session.get(`${BASE_URL}/product/${product_id}`);
      expect(response.status).to.equal(200);

      const data = {
        product_id,
        quantity: getRandomQuantity()
      };
      const addToCartResponse = await session.post(`${BASE_URL}/cart`, data);
      expect(addToCartResponse.status).to.equal(200);
    }
  } catch (error) {
    throw error;
  }
}

async function testCheckout(session) {
  try {
    for (const product_id of products) {
      const data = {
        product_id,
        quantity: getRandomQuantity(),
        email: 'someone@example.com',
        street_address: '1600 Amphitheatre Parkway',
        zip_code: '94043',
        city: 'Mountain View',
        state: 'CA',
        country: 'United States',
        credit_card_number: '4432-8015-6152-0454',
        credit_card_expiration_month: '1',
        credit_card_expiration_year: '2039',
        credit_card_cvv: '672'
      };
      const checkoutResponse = await session.post(`${BASE_URL}/cart/checkout`, data);
      expect(checkoutResponse.status).to.equal(200);
    }
  } catch (error) {
    throw error;
  }
}
