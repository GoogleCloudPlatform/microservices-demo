# cartservice

## Environment Variables

`REDIS_SPAN_ERROR_RATE`: float [0, 1], Percentage of redis spans that will be flagged as an error

`EXTERNAL_DB_NAME`: string, Name of external database
`EXTERNAL_DB_ACCESS_RATE`: float [0, 1], Percentage of redis spans that will be turned into external database spans
`EXTERNAL_DB_MAX_DURATION_MILLIS`: int, Artificial delay added to external database spans (mock value)

## Building and Testing Locally

Use the `dotnet` tool to build the project locally:

```
$ dotnet build
```

After source changes are done, build the Docker image and validate it using `docker-compose`
and the test project:

```
$ pushd ./tests/
$ docker build -t cartservice ./..
$ docker-compose up -d
$ dotnet test .
$ docker-compose down
$ popd
```

If you want to send data to the backend set the following environment below when starting the `docker-compose`:

  * `SPLUNK_ACCESS_TOKEN`
  * `SIGNALFX_ENV`
