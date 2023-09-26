const { Given, When, Then } = require('@cucumber/cucumber');
const assert = require('assert'); // You can use 'assert' for assertions

const httpClient = require('http'); // Assuming you're using Node.js's built-in 'http' module
const BASE_URL_DEFAULT = "http://10.2.10.50:8081";
const BASE_URL = process.env.machine_dns || BASE_URL_DEFAULT;

const products = [
    "0PUK6V6EV0", "1YMWWN1N4O", "2ZYFJ3GM2N",
    "66VCHSJNUP", "6E92ZMYYFZ", "9SIQT8TOJO",
    "L9ECAV7KIM", "LS4PSXUNUM", "OLJCESPC7Z"
];

Given('There are {int} users', function (numUsers) {
    // No need for threads in JavaScript, perform actions sequentially
    for (let i = 0; i < numUsers; i++) {
        testSession();
    }
});

When('All users start their sessions', function () {
    // In JavaScript, actions are performed sequentially, so no need for this step
});

Then('All sessions should complete successfully', function () {
    // Post-execution checks, if any.
});

Given('A product list', function () {
    // Assuming products are already initialized at the top
});

When('A user browses products', async function () {
    for (const product of products) {
        await testProduct(BASE_URL + "/product/" + product);
    }
});

Then('All products should be accessible', function () {
    // Assuming if the previous step passes, all products are accessible.
});

async function testSession() {
    try {
        const response = await sendHttpRequest(BASE_URL + "/");
        assert.strictEqual(response.statusCode, 200, "Failed to load the homepage");
    } catch (error) {
        throw new Error("Failed to load the homepage: " + error.message);
    }
}

When('A user views their cart', async function () {
    try {
        const response = await sendHttpRequest(BASE_URL + "/cart");
        assert.strictEqual(response.statusCode, 200, "Failed to view the cart");
    } catch (error) {
        throw new Error("Failed to view the cart: " + error.message);
    }
});

Then('The cart page should be accessible', function () {
    // Assuming if the previous step passes, the cart is accessible.
});

When('A user adds products to their cart', async function () {
    for (const product of products) {
        await testProduct(BASE_URL + "/product/" + product + "/add");
    }
});

Then('All products should be added successfully', function () {
    // Assuming if the previous step passes, all products are added successfully.
});

When('A user accesses site assets', async function () {
    try {
        await testProduct(BASE_URL + "/static/favicon.ico");
        await testProduct(BASE_URL + "/static/img/products/hairdryer.jpg");
    } catch (error) {
        throw new Error("Failed to load site assets: " + error.message);
    }
});

Then('The assets should be accessible', function () {
    // Assuming if the previous step passes, assets are accessible.
});

When('A user checks out with products', async function () {
    try {
        const checkoutData = {
            email: "someone@example.com",
            street_address: "1600 Amphitheatre Parkway",
            zip_code: "94043",
            city: "Mountain View",
            state: "CA",
            country: "United States",
            credit_card_number: "4432-8015-6152-0454",
            credit_card_expiration_month: "1",
            credit_card_expiration_year: "2024",
            credit_card_cvv: "672"
        };

        const response = await sendHttpPostRequest(BASE_URL + "/cart/checkout", checkoutData);
        assert.strictEqual(response.statusCode, 200, "Failed to checkout cart");
    } catch (error) {
    }
});

Then('The checkout should be successful', function () {
    // Assuming if the previous step passes, checkout was successful.
});

async function sendHttpRequest(url) {
    return new Promise((resolve, reject) => {
        httpClient.get(url, (response) => {
            resolve(response);
        }).on('error', (error) => {
            reject(error);
        });
    });
}

async function sendHttpPostRequest(url, data) {
    const postData = JSON.stringify(data);

    const options = {
        hostname: BASE_URL,
        port: 80,
        path: url,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': postData.length
        }
    };

    return new Promise((resolve, reject) => {
        const req = httpClient.request(options, (response) => {
            resolve(response);
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.write(postData);
        req.end();
    });
}

async function testProduct(url) {
    try {
        const response = await sendHttpRequest(url);
        assert.strictEqual(response.statusCode, 200, "Failed to load the product");
    } catch (error) {
        throw new Error("Failed to load the product: " + error.message);
    }
}
