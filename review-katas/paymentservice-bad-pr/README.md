# Paymentservice Bad PR

This package preserves the intentionally problematic `paymentservice` exercise in an isolated training area.

## Contents

- `discount.js` contains duplicated logic, global state, filesystem coupling, and edge-case bugs.
- `discount.test.js` contains randomness, timing assumptions, date sensitivity, and test-order coupling.

## Run

```bash
cd review-katas/paymentservice-bad-pr
npm test
```

This package is for review practice only.
