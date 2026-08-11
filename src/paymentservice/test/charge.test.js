// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

const assert = require('assert');
const charge = require('../charge');

// Valid test credit card (VISA test number)
const validCard = {
  credit_card_number: '4111111111111111',
  credit_card_expiration_month: 12,
  credit_card_expiration_year: new Date().getFullYear() + 1,
  credit_card_cvv: 123
};

const validAmount = { currency_code: 'USD', units: 100, nanos: 500000000 };

describe('Payment charge', () => {
  it('should process a valid charge', () => {
    const result = charge({ amount: validAmount, credit_card: validCard });
    assert.ok(result.transaction_id, 'should return a transaction_id');
  });

  it('should reject NaN amount units', () => {
    assert.throws(
      () => charge({ amount: { ...validAmount, units: NaN }, credit_card: validCard }),
      /Invalid payment amount/
    );
  });

  it('should reject NaN amount nanos', () => {
    assert.throws(
      () => charge({ amount: { ...validAmount, nanos: NaN }, credit_card: validCard }),
      /Invalid payment amount/
    );
  });

  it('should reject missing amount', () => {
    assert.throws(
      () => charge({ credit_card: validCard }),
      /Invalid payment amount/
    );
  });

  it('should reject non-numeric amount units', () => {
    assert.throws(
      () => charge({ amount: { ...validAmount, units: 'abc' }, credit_card: validCard }),
      /Invalid payment amount/
    );
  });
});
