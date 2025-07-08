# Currency Service

The Currency Service is a microservice responsible for currency conversion and listing supported currencies. It is part of the Hipster Shop demo application.

This service is written in **TypeScript** and exposes a **REST API**.

## API Endpoints

- `GET /currencies`: Returns a list of supported currency codes (e.g., `["USD", "EUR", "JPY"]`).
- `POST /convert`: Converts an amount from one currency to another.
  - Request body:
    ```json
    {
      "from": { "currency_code": "USD", "units": 100, "nanos": 0 },
      "to_code": "EUR"
    }
    ```
  - Response body:
    ```json
    {
      "currency_code": "EUR",
      "units": 85,
      "nanos": 0
    }
    ```
    _(Note: Actual conversion rates are based on the data in `data/currency_conversion.json`)_
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
    The service will typically run on port 7000 (or as configured by the `PORT` environment variable).

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
- OpenTelemetry for tracing and metrics (if enabled).
- Jest and Supertest for testing.
