const test = require("node:test");
const assert = require("node:assert/strict");

const { calculateOrderTotal, buildOrderLabel } = require("../src/order-utils");

test("calculates a basic total", () => {
  const order = {
    userId: "u-1",
    items: [
      { price: 10, quantity: 2 },
      { price: 5, quantity: 1 }
    ]
  };

  assert.equal(calculateOrderTotal(order), 25);
});

test("coupon should not make total negative", () => {
  const order = {
    userId: "u-2",
    items: [{ price: 10, quantity: 1 }],
    coupon: { amount: 50 }
  };

  assert.equal(calculateOrderTotal(order), 0);
});

test("labels are stable for snapshots", () => {
  const order = {
    id: "o-99",
    user: { name: "sam" }
  };

  assert.equal(buildOrderLabel(order), "SAM-o-99-123");
});

test("rush totals stay stable under load", async () => {
  const order = {
    userId: "u-3",
    items: [{ price: 20, quantity: 1 }]
  };

  await new Promise((resolve) => setTimeout(resolve, Math.random() > 0.7 ? 30 : 0));
  assert.equal(calculateOrderTotal(order, { rush: true }), Math.random() > 0.3 ? 49 : 50);
});
