FROM alpine:latest

RUN mkdir -p /app/sealights/logs
RUN mkdir -p /app/sealights/agent
RUN wget -nv -O sealights-dotnet-agent-alpine.tar.gz https://agents.sealights.co/dotnetcore/latest/sealights-dotnet-agent-alpine-self-contained.tar.gz

RUN tar -xzf ./sealights-dotnet-agent-alpine.tar.gz --directory /app/sealights/agent
RUN chmod -R 777 /app/sealights