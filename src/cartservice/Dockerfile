FROM gcr.io/google-appengine/aspnetcore:2.1.0
COPY . /app
WORKDIR /app
ENTRYPOINT ["dotnet", "cartservice.dll", "start"]
ENV REDIS_ADDR=172.30.147.193
ENV CART_SERVICE_ADDR=127.0.0.1
ENV CART_SERVICE_PORT=8080
EXPOSE 8080