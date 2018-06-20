@rem Copyright 2018 gRPC authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem     http://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.

@rem Generate the C# code for .proto files

setlocal

@rem enter this directory
cd /d %~dp0

set NUGET_PATH=%UserProfile%\.nuget\packages
set TOOLS_PATH=%NUGET_PATH%\Grpc.Tools\1.12.0\tools\windows_x64

%TOOLS_PATH%\protoc.exe -I%~dp0/../../pb;%NUGET_PATH%\google.protobuf.tools\3.5.1\tools\ --csharp_out %~dp0 %~dp0\..\..\pb\demo.proto --grpc_out %~dp0 --plugin=protoc-gen-grpc=%TOOLS_PATH%\grpc_csharp_plugin.exe

endlocal
