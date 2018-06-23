@echo off

set REDIS_PORT=6379
set REDIS_ADDR=172.30.147.193
set CART_SERVICE_ADDR=127.0.0.1
set CART_SERVICE_PORT=7070

rem run docker container with redis
rem docker run -d --name=redis -p %REDIS_PORT%:%REDIS_PORT% redis:alpine

rem run docker container with cart service
docker run -it --rm -e REDIS_ADDR=%REDIS_ADDR%:%REDIS_PORT% -e CART_SERVICE_ADDR=%CART_SERVICE_ADDR% -e CART_SERVICE_PORT=%CART_SERVICE_PORT% -p %CART_SERVICE_PORT%:%CART_SERVICE_PORT% cartservice
rem -e GRPC_TRACE=all -e GRPC_VERBOSITY=debug