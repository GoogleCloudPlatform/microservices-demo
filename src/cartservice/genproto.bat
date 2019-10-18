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

@rem Generate the C# code for .proto files

setlocal

@rem enter this directory
cd /d %~dp0

set NUGET_PATH=%UserProfile%\.nuget\packages
set TOOLS_PATH=%NUGET_PATH%\Grpc.Tools\1.12.0\tools\windows_x64

%TOOLS_PATH%\protoc.exe -I%~dp0/../../pb;%NUGET_PATH%\google.protobuf.tools\3.5.1\tools\ --csharp_out %~dp0\grpc_generated %~dp0\..\..\pb\demo.proto --grpc_out %~dp0\grpc_generated --plugin=protoc-gen-grpc=%TOOLS_PATH%\grpc_csharp_plugin.exe

endlocal
