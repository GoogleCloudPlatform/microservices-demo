# https://mcr.microsoft.com/v2/dotnet/sdk/tags/list
FROM mcr.microsoft.com/dotnet/sdk:7.0.306@sha256:94e91c9e8349b4caba454beb630cf05b56ee3a985e6c0c967ce57f5c58537033 as builder
WORKDIR /app
COPY cartservice.csproj .
RUN dotnet restore cartservice.csproj -r linux-musl-x64
COPY . .
RUN dotnet publish cartservice.csproj -p:PublishSingleFile=false -r linux-musl-x64 --self-contained true -p:PublishTrimmed=True -p:TrimMode=Link -c release -o /cartservice --no-restore
# https://mcr.microsoft.com/v2/dotnet/runtime-deps/tags/list
FROM mcr.microsoft.com/dotnet/runtime-deps:7.0.9-alpine3.18-amd64@sha256:f855dffa26e6681a7a8ee038a0877afab43ffaf70c1cae3a526c4eadc33bbdf5
WORKDIR /app
COPY start-app.sh .
ARG BRANCH
ARG AGENT_URL="https://agents.sealights.co/dotnetcore/latest/sealights-dotnet-agent-alpine-self-contained.tar.gz"
ENV BUILD_NAME="hello"

# Sealights - install prereq, agent, token, bsid
# Best practice it to mount a pre-existing sealights directory depending on the environment (test or prod)


COPY --from=builder /cartservice .
EXPOSE 7070
ENV DOTNET_EnableDiagnostics=0 \
  ASPNETCORE_URLS=http://*:7070
ENV BRANCH=${BRANCH}
USER 1000
CMD export BUILD_NAME="${BUILD_NAME}" && export BRANCH="${BRANCH}" && sh start-app.sh /app/cartservice