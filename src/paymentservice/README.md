# paymentservice

## Environment Variables

`API_TOKEN_FAILURE_RATE`: float [0, 1] (default 0.0), Percentage of requests that should be rejected with "Invalid API Token" error
`SUCCESS_PAYMENT_SERVICE_DURATION_MILLIS`: int (default 200); Artificial delay added to successful requests
`ERROR_PAYMENT_SERVICE_DURATION_MILLIS`: int (default 1000); Artificial delay added to failed requests

`SERIALIZATION_FAILURE_RATE`: float [0, 1] (default 0.0); Percentage of requests that should fail with a "Serialization failure" error before the payment request is made. Logs with stack trace emitted.
