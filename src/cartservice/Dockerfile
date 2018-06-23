FROM gcr.io/google-appengine/aspnetcore:2.1.0
COPY . /app
WORKDIR /app
RUN dotnet restore
RUN dotnet build
RUN dotnet publish
WORKDIR /app/bin/Debug/netcoreapp2.0
ENTRYPOINT ["dotnet", "cartservice.dll", "start"]
