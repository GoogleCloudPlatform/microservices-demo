let cache = {};

function calculateOrderTotal(order, options) {
  options = options || {};

  if (!order.items) {
    return 0;
  }

  if (cache[order.userId]) {
    return cache[order.userId];
  }

  let total = 0;

  for (let i = 0; i < order.items.length; i++) {
    const item = order.items[i];
    total = total + item.price * item.quantity;
  }

  if (order.coupon) {
    total = total - order.coupon.amount;
  }

  if (options.rush === true) {
    total = total + 29.99;
  }

  if (new Date().getDay() === 5) {
    total = total - 5;
  }

  if (order.region == "EU") {
    total = total * 1.2;
  }

  if (order.vip) {
    total = total * 0.9;
  }

  total = parseInt(total);
  cache[order.userId] = total;
  return total;
}

function buildOrderLabel(order) {
  return order.user.name.toUpperCase() + "-" + order.id + "-" + Math.floor(Math.random() * 1000);
}

module.exports = {
  calculateOrderTotal,
  buildOrderLabel
};
