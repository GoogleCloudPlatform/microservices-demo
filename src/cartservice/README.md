# cartservice

## Configuration Environment Variables

These environment variables control the behavior of the application.
They make the application exercise different features available in the Splunk Observability.

### Synthetic External DB Access

These environment variables are used to simulate access to an external DB for some of the requests.
The access to DB is wrapped by OpenTracing spans and the backend infers an external DB from these spans.

- `EXTERNAL_DB_ACCESS_RATE`: float [0, 1], percentage of redis spans that will be turned into external database spans
- `EXTERNAL_DB_ERROR_RATE`: float [0, 1], percentage of external DB access spans that will report error
- `EXTERNAL_DB_MAX_DURATION_MILLIS`: int, artificial maximum delay randomly added to external database spans (mock value)
- `EXTERNAL_DB_NAME`: string, name of external database

### Optimizations

These environment variables are used to trigger behaviors on the application that affect its perfomance characteristics.
Each optimization affects lantency, CPU, and memory in different ways.
Keep that in mind when interpreting their effect.
All these environment variables are boolean.

- `FIX_EXCESSIVE_ALLOCATION`: bool, controls if the excessive allocation per request should be happening or not
- `FIX_SLOW_LEAK`: bool, controls if a slowly growing memory leak is going to be happening or not
- `OPTIMIZE_CPU`: bool, controls if  the CPU is going to be efficiently used during input validation
- `OPTIMIZE_BLOCKING`: bool, controls if the code is going to do some blocking to retrieve a handle to the Redis DB

## Building and Testing Locally

Use the `dotnet` tool to build the project locally:

```bash
dotnet build
```

After source changes are done, build the Docker image and validate it using `docker-compose`
and the test project:

```bash
pushd ./tests/
docker build -t cartservice ./..
docker-compose up -d
dotnet test .
docker-compose down
popd
```

If you want to send data to the backend set the following environment below when starting the `docker-compose`:

- `SPLUNK_ACCESS_TOKEN`
- `SIGNALFX_ENV`
