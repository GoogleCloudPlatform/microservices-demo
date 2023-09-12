#!/bin/sh
# Check if sealights folder exists
if [ -d "/app/sealights/" ]; then
  /app/sealights/agent/SL.DotNet cdAgent --appName cartservice --branchName main --buildName ${BUILD_NAME} \
         --binDir /app  --includeNamespace *.services* --target $1 --token ${SL_TOKEN} --workingDir /app \
         --identifyMethodsByFqn --labId ${SL_LAB_ID}
else
  dotnet $1
fi
