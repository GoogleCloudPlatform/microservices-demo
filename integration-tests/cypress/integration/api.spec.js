describe('Api Tests', () => {
  const BASE_URL = 'http://10.2.10.50:8081';

  it('should return 200 for index page', () => {
    cy.request({
      method: 'GET',
      url: BASE_URL + '/',
    }).then(response => {
      expect(response.status).to.equal(200);
    });
  });

  it('should be able to set different currencies', () => {
    const currencies = ['EUR', 'USD', 'JPY', 'CAD'];
    for (const currency of currencies) {
      cy.request({
        method: 'POST',
        url: BASE_URL + '/setCurrency',
        body: { currency_code: currency },
      }).then(response => {
        expect(response.status).to.equal(200);
      });
    }
  });

  it('should return 200 for browsing products', () => {
    const products = [
      '0PUK6V6EV0',
      '1YMWWN1N4O',
      // ... other product IDs
    ];

    for (const product_id of products) {
      cy.request({
        method: 'GET',
        url: BASE_URL + `/product/${product_id}`,
      }).then(response => {
        expect(response.status).to.equal(200);
      });
    }
  });

  it('should return 404 for a non-existent route', () => {
    cy.request({
      url: BASE_URL + '/nonexistent-route',
      failOnStatusCode: false,
    }).then(response => {
      expect(response.status).to.equal(404);
    });
  });

  it('should return 400 for invalid request data', () => {
    cy.request({
      method: 'POST',
      url: BASE_URL + '/setCurrency',
      body: { invalid_key: 'invalid_value' },
      failOnStatusCode: false,
    }).then(response => {
      expect(response.status).to.equal(400);
    });
  });
});
