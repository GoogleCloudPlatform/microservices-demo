@echo off

set ENV=%1

IF %ENV%==local GOTO local
IF %ENV%==docker GOTO  docker_local
GOTO End1

:local
  set REDIS_PORT=6379
  set REDIS_ADDR=localhost:%REDIS_PORT%
  set LISTEN_ADDR=0.0.0.0
  set PORT=7070

  echo running redis emulator locally on a separate window
  taskkill /f /im "redis-server.exe"
  start redis-server

  echo running the cart service locally
  dotnet build ..\.
  dotnet run --project ../cartservice.csproj start
GOTO End1

:docker_local
  set REDIS_PORT=6379
  set REDIS_ADDR=0.0.0.0:%REDIS_PORT%
  set LISTEN_ADDR=0.0.0.0
  set PORT=7070

  echo run docker container with redis
  start docker run -d --name=redis -p %REDIS_PORT%:%REDIS_PORT% redis

  echo building container image for cart service
  docker build -t cartservice ..\.

  echo run container image for cart service
  docker run -it --rm -e REDIS_ADDR=%REDIS_ADDR% -e LISTEN_ADDR=%LISTEN_ADDR% -e PORT=%PORT% -p %PORT%:%PORT% cartservice

GOTO End1

:End1

rem run docker container with cart service
rem docker run -it --rm -e REDIS_ADDR=%REDIS_ADDR%:%REDIS_PORT% -e CART_SERVICE_ADDR=%CART_SERVICE_ADDR% -e CART_SERVICE_PORT=%CART_SERVICE_PORT% -p %CART_SERVICE_PORT%:%CART_SERVICE_PORT% cartservice
rem -e GRPC_TRACE=all -e GRPC_VERBOSITY=debug
