# Payment Service

The Payment Service is a microservice responsible for processing credit card payments. It is part of the Hipster Shop demo application.

This service is written in **TypeScript** and exposes a **REST API**.

## API Endpoints

- `POST /charge`: Processes a credit card payment.
  - Request body:
    ```json
    {
      "amount": { "currency_code": "USD", "units": 120, "nanos": 500000000 },
      "credit_card": {
        "credit_card_number": "4000000000000000",
        "credit_card_cvv": 123,
        "credit_card_expiration_year": 2028,
        "credit_card_expiration_month": 10
      }
    }
    ```
  - Successful response body (200 OK):
    ```json
    {
      "transaction_id": "some-uuid-string"
    }
    ```
  - Error response body (e.g., 400 Bad Request for invalid card):
    ```json
    {
      "message": "Credit card info is invalid",
      "errorType": "InvalidCreditCard"
    }
    ```
- `GET /health`: Health check endpoint. Returns `{"status": "SERVING"}`.

## Running Locally

1.  **Install dependencies:**
    ```bash
    npm install
    ```
2.  **Build the TypeScript code:**
    ```bash
    npm run build
    ```
3.  **Start the service:**
    ```bash
    npm start
    ```
    The service will typically run on port 50051 (or as configured by the `PORT` environment variable).

## Running Tests

```bash
npm test
```

This will execute Jest unit tests and generate a coverage report in the `coverage/` directory.

## Dependencies

Key dependencies include:
- Express.js for the REST API framework.
- TypeScript for static typing.
- Pino for logging.
- `simple-card-validator` for basic credit card validation.
- `uuid` for generating transaction IDs.
- OpenTelemetry for tracing and metrics (if enabled).
- Jest and Supertest for testing.
