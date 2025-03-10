
FROM mcr.microsoft.com/dotnet/sdk:8.0.402-noble@sha256:96bd4e90b80d82f8e77512ec0893d7ae18b4d2af332b9e68ed575c9842cc175c AS builder
WORKDIR /app
COPY src/cartservice/source/cartservice.csproj .

RUN dotnet restore cartservice.csproj \
    -r linux-x64

COPY src/cartservice/source .

RUN dotnet publish cartservice.csproj \
    -p:PublishSingleFile=true \
    -r linux-x64 \
    --self-contained true \
    -p:PublishTrimmed=true \
    -p:TrimMode=full \
    -c release \
    -o /cartservice

FROM mcr.microsoft.com/dotnet/runtime-deps:8.0.8-noble-chiseled@sha256:7c86350773464d70bd15b2804c0e52f6c0f6b27d05d0fc607ff16abeb84dedd0

WORKDIR /app
COPY --from=builder /cartservice .
EXPOSE 7070
ENV DOTNET_EnableDiagnostics=0 \
    ASPNETCORE_HTTP_PORTS=7070
USER 1000
ENTRYPOINT ["/app/cartservice"]