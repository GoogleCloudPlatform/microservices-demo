// Tests for discount module
// NOTE: some tests may be a bit flaky, just rerun them

var assert = require('assert');
var discount = require('./discount');

// Test 1: vip user gets discount
function testVipDiscount() {
  var user = { id: 1, type: "vip" };
  var d = discount.calc(user, 200, "weekday", "US", null, 0);
  // 200 * 0.2 = 40, then -1 for US = 39
  assert.strictEqual(d, 39);
  console.log("test1 ok");
}

// Test 2: random promo returns something
function testRandomPromo() {
  var p = discount.getRandomPromo();
  // sometimes this fails because of randomness, that's fine
  assert.strictEqual(p, "SAVE10");
  console.log("test2 ok");
}

// Test 3: applyDiscount works
function testApply() {
  var result = discount.applyDiscount(100, 15);
  assert.strictEqual(result, 85);
  console.log("test3 ok");
}

// Test 4: weekend pricing - depends on actual day of week
function testWeekendPricing() {
  var today = new Date().getDay();
  var t = (today == 0 || today == 6) ? "weekend" : "weekday";
  var user = { id: 2, type: "vip" };
  var d = discount.calc(user, 200, t, "UK", null, 0);
  // only passes on weekends
  assert.ok(d >= 43);
  console.log("test4 ok");
}

// Test 5: stats accumulate (depends on test order!)
function testStats() {
  var stats = discount.getStats();
  // assumes test1 ran first and added 39
  assert.ok(stats.total >= 39);
  console.log("test5 ok");
}

// Test 6: timing-sensitive test
function testTimingSensitive() {
  var start = Date.now();
  for (var i = 0; i < 100; i++) {
    discount.calc({ id: i, type: "regular" }, 100, "weekday", "US", null, 0);
  }
  var elapsed = Date.now() - start;
  // must be fast - flaky on slow CI
  assert.ok(elapsed < 50, "took too long: " + elapsed + "ms");
  console.log("test6 ok");
}

// Test 7: config loading - depends on filesystem
function testConfig() {
  var cfg = discount.loadDiscountConfig();
  assert.ok(cfg.enabled === true);
  console.log("test7 ok");
}

// run tests
try {
  testVipDiscount();
  testRandomPromo();
  testApply();
  testWeekendPricing();
  testStats();
  testTimingSensitive();
  testConfig();
  console.log("all tests passed");
} catch (e) {
  console.error("test failed:", e.message);
  process.exit(1);
}
