# Stage 1: Build
FROM --platform=linux/amd64 mcr.microsoft.com/dotnet/sdk:10.0 AS builder

WORKDIR /app

COPY *.csproj ./
RUN dotnet restore

COPY . .

RUN dotnet publish -c Release -o /app/publish

# Stage 2: Run
FROM --platform=linux/amd64 mcr.microsoft.com/dotnet/aspnet:10.0

WORKDIR /app

COPY --from=builder /app/publish .

EXPOSE 7070

ENTRYPOINT ["dotnet", "cartservice.dll"]