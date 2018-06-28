FROM gcr.io/google-appengine/aspnetcore:2.1.0
COPY . /app
WORKDIR /app
RUN dotnet restore
RUN dotnet build
RUN dotnet publish
WORKDIR /app/bin/Debug/netcoreapp2.0
ENV PORT 7070
EXPOSE 7070
ENTRYPOINT ["dotnet", "cartservice.dll", "start"]
