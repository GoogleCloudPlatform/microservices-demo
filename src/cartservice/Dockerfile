FROM golang:1.10 as probe
RUN wget -qO/go/bin/dep https://github.com/golang/dep/releases/download/v0.5.0/dep-linux-amd64 && \
    chmod +x /go/bin/dep
ENV PROJECT github.com/GoogleCloudPlatform/microservices-demo/src/cartservice/probe
WORKDIR /go/src/$PROJECT
COPY probe/Gopkg.* ./
RUN dep ensure --vendor-only -v
COPY ./probe ./
RUN go build -o /cartservice_probe .

FROM microsoft/dotnet:2.1-sdk-alpine as builder
WORKDIR /app
COPY . .
RUN dotnet restore && \
    dotnet build && \
    dotnet publish -c release -r linux-musl-x64 -o /cartservice

# cartservice
FROM alpine:3.8
# Add the probe
COPY --from=probe /cartservice_probe /cartservice_probe
# Dependencies for runtime
# busybox-extras => telnet
RUN apk add --no-cache \
    busybox-extras \
    libc6-compat \
    libunwind \
    libuuid \
    libgcc \
    libstdc++ \
    libintl \
    icu
WORKDIR /app
COPY --from=builder /cartservice .
ENTRYPOINT ["./cartservice", "start"]