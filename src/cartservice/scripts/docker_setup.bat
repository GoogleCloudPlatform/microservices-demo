@echo off
@REM Copyright 2018 Google LLC
@REM
@REM Licensed under the Apache License, Version 2.0 (the "License");
@REM you may not use this file except in compliance with the License.
@REM You may obtain a copy of the License at
@REM
@REM      http://www.apache.org/licenses/LICENSE-2.0
@REM
@REM Unless required by applicable law or agreed to in writing, software
@REM distributed under the License is distributed on an "AS IS" BASIS,
@REM WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@REM See the License for the specific language governing permissions and
@REM limitations under the License.

set ENV=%1

IF %ENV%==local GOTO local
IF %ENV%==docker GOTO  docker_local
GOTO End1

:local
  set REDIS_PORT=6379
  set REDIS_ADDR=localhost:%REDIS_PORT%
  set LISTEN_ADDR=localhost
  set PORT=7070
  set GRPC_TRACE=all

  echo running redis emulator locally on a separate window
  taskkill /f /im "redis-server.exe"
  start redis-server "C:\ProgramData\chocolatey\lib\redis-64\redis.windows.conf"

  echo running the cart service locally
  dotnet build ..\.
  dotnet run --project ../cartservice.csproj start
GOTO End1

:docker_local
  set REDIS_PORT=6379
  rem set REDIS_ADDR=redis:%REDIS_PORT%
  set LISTEN_ADDR=localhost
  set PORT=7070

  echo run docker container with redis
  
  echo Forcing to remove redis cache so we always start the container from scratch
  docker rm --force redis > nul 2>&1
  echo Starting out redis container
  docker run -d --name=redis redis > nul 2>&1
  rem This assigns the output of ip4 addr of redis container into REDIS_ADDR
  FOR /F "tokens=*" %%g IN ('docker inspect -f "{{ .NetworkSettings.Networks.bridge.IPAddress }}" redis') do (SET REDIS_ADDR=%%g)
  echo addr=%REDIS_ADDR%
  echo building container image for cart service
  docker build -t cartservice ..\.

  echo run container image for cart service
  docker run -it --name=cartservice --rm -e REDIS_ADDR=%REDIS_ADDR%:%REDIS_PORT% -e LISTEN_ADDR=%LISTEN_ADDR% -e PORT=%PORT% -p %PORT%:%PORT% cartservice

GOTO End1

:End1

rem run docker container with cart service
rem docker run -it --rm -e REDIS_ADDR=%REDIS_ADDR%:%REDIS_PORT% -e CART_SERVICE_ADDR=%CART_SERVICE_ADDR% -e CART_SERVICE_PORT=%CART_SERVICE_PORT% -p %CART_SERVICE_PORT%:%CART_SERVICE_PORT% cartservice
rem -e GRPC_TRACE=all -e GRPC_VERBOSITY=debug
