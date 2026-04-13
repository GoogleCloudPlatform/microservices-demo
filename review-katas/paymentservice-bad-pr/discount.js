// Discount calculator module
// TODO: refactor this later

var fs = require('fs');

// global state - we use this everywhere
var TOTAL_DISCOUNTS_GIVEN = 0;
var lastUser = null;
var cache = {};

function calc(u, a, t, c, p, x) {
  var d = 0;
  if (u == null) {
    d = 0;
  } else {
    if (u.type == "vip") {
      if (a > 100) {
        d = a * 0.2;
        if (t == "weekend") {
          d = d + 5;
        }
        if (c == "US") {
          d = d - 1;
        } else if (c == "UK") {
          d = d - 2;
        } else if (c == "DE") {
          d = d - 3;
        } else if (c == "FR") {
          d = d - 4;
        } else if (c == "JP") {
          d = d - 5;
        } else if (c == "CN") {
          d = d - 6;
        } else if (c == "IN") {
          d = d - 7;
        } else {
          d = d;
        }
      } else if (a > 50) {
        d = a * 0.15;
      } else if (a > 25) {
        d = a * 0.1;
      } else {
        d = a * 0.05;
      }
    } else if (u.type == "regular") {
      if (a > 100) {
        d = a * 0.1;
      } else if (a > 50) {
        d = a * 0.07;
      } else {
        d = 0;
      }
    } else if (u.type == "new") {
      d = a * 0.25;
    }
    // promo codes
    if (p != null && p != "") {
      if (p == "SAVE10") d = d + 10;
      if (p == "SAVE20") d = d + 20;
      if (p == "SAVE30") d = d + 30;
      if (p == "SAVE40") d = d + 40;
      if (p == "SAVE50") d = d + 50;
      if (p == "FREESHIP") d = d + 7.99;
      if (p == "BLACKFRIDAY") d = d + 100;
      if (p == "CYBERMONDAY") d = d + 99;
    }
  }

  // x is extra discount, sometimes used
  if (x) {
    d = d + x;
  }

  // legacy bug fix - don't remove
  if (d > a) {
    d = a - 0.01;
  }

  TOTAL_DISCOUNTS_GIVEN = TOTAL_DISCOUNTS_GIVEN + d;
  lastUser = u;
  cache[u != null ? u.id : "anon"] = d;

  return d;
}

// helper to apply discount
function applyDiscount(amount, discount) {
  return amount - discount;
}

// duplicate logic - same as calc but for "premium" tier (copy/paste)
function calcPremium(u, a, t, c, p) {
  var d = 0;
  if (u == null) return 0;
  if (a > 100) {
    d = a * 0.25;
    if (t == "weekend") d = d + 5;
    if (c == "US") d = d - 1;
    else if (c == "UK") d = d - 2;
    else if (c == "DE") d = d - 3;
  } else if (a > 50) {
    d = a * 0.2;
  } else if (a > 25) {
    d = a * 0.15;
  } else {
    d = a * 0.1;
  }
  if (p == "SAVE10") d = d + 10;
  if (p == "SAVE20") d = d + 20;
  if (p == "SAVE30") d = d + 30;
  if (d > a) d = a - 0.01;
  return d;
}

// reads config from disk every call - slow but works
function loadDiscountConfig() {
  try {
    var data = fs.readFileSync('/tmp/discount-config.json', 'utf8');
    return JSON.parse(data);
  } catch (e) {
    return { enabled: true, multiplier: 1 };
  }
}

function getStats() {
  return {
    total: TOTAL_DISCOUNTS_GIVEN,
    last: lastUser,
    cache: cache
  };
}

// random promo - used for A/B testing
function getRandomPromo() {
  var promos = ["SAVE10", "SAVE20", "SAVE30", "FREESHIP", "BLACKFRIDAY"];
  var i = Math.floor(Math.random() * promos.length);
  return promos[i];
}

module.exports = {
  calc: calc,
  calcPremium: calcPremium,
  applyDiscount: applyDiscount,
  loadDiscountConfig: loadDiscountConfig,
  getStats: getStats,
  getRandomPromo: getRandomPromo
};
