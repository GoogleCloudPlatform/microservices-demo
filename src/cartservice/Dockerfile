FROM gcr.io/google-appengine/aspnetcore:2.1.0
COPY . /app
WORKDIR /app
RUN dotnet restore
RUN dotnet build
RUN dotnet publish
WORKDIR /app/bin/Debug/netcoreapp2.0
RUN apt update && apt install net-tools telnet
ENTRYPOINT ["dotnet", "cartservice.dll", "start"]
