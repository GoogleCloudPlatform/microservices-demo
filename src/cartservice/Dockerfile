# cartservice_probe
FROM golang:1.10 as builder
RUN wget -qO/go/bin/dep https://github.com/golang/dep/releases/download/v0.5.0/dep-linux-amd64 && \
      chmod +x /go/bin/dep
ENV PROJECT github.com/GoogleCloudPlatform/microservices-demo/src/cartservice/probe
WORKDIR /go/src/$PROJECT
COPY probe/Gopkg.* ./
RUN dep ensure --vendor-only -v
COPY ./probe ./
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
