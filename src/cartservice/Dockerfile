# cartservice_probe
FROM golang:1.10 as builder
WORKDIR /src/microservices-demo/cartservice/probe
COPY probe/ .
RUN go get -d ./...
RUN go build -o /cartservice_probe .

# cartservice
FROM gcr.io/google-appengine/aspnetcore:2.1.0
COPY --from=builder /cartservice_probe /cartservice_probe
RUN apt-get update && apt-get install net-tools telnet
WORKDIR /app
COPY . .
RUN dotnet restore && \
    dotnet build && \
    dotnet publish
WORKDIR /app/bin/Debug/netcoreapp2.0
ENTRYPOINT ["dotnet", "cartservice.dll", "start"]
