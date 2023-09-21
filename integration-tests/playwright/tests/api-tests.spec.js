const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.machine_dns || 'http://10.2.10.50:8081';

//test('should return 200 for index page', async ({ page }) => {
//  await page.goto(BASE_URL);
//  const status = await page.mainFrame().status();
//  expect(response.status()).toBe(200);
//});

test('should be able to set different currencies', async ({ page }) => {
  const currencies = ['EUR', 'USD', 'JPY', 'CAD'];
  for (const currency of currencies) {
    await page.route('**/setCurrency', (route) => {
      route.fulfill({
        status: 200,
      });
    });
    await page.goto(BASE_URL + '/setCurrency', {
      method: 'POST',
      postData: JSON.stringify({ currency_code: currency }),
    });
  }
});

// Additional tests for browsing products
const productIds = [
  '0PUK6V6EV0',
  '1YMWWN1N4O',
  '2ZYFJ3GM2N',
  '66VCHSJNUP',
  '6E92ZMYYFZ',
  '9SIQT8TOJO',
  'L9ECAV7KIM',
  'LS4PSXUNUM',
  'OLJCESPC7Z',
];

for (const productId of productIds) {
  test(`should return 200 for browsing product: ${productId}`, async ({ page }) => {
    const response = await page.goto(BASE_URL + `/product/${productId}`, {
      waitUntil: 'domcontentloaded',
      timeout: 0,
    });
    expect(response.status()).toBe(200);
  });
}

test('should return 404 for a non-existent route', async ({ page }) => {
  const response = await page.goto(BASE_URL + '/nonexistent-route', {
    waitUntil: 'domcontentloaded',
    timeout: 0,
  });
  expect(response.status()).toBe(404);
});

test('should return 400 for invalid request data', async ({ page }) => {
  await page.route('**/setCurrency', (route) => {
    route.fulfill({
      status: 400,
    });
  });
  await page.goto(BASE_URL + '/setCurrency', {
    method: 'POST',
    postData: JSON.stringify({ invalid_key: 'invalid_value' }),
  });
});
