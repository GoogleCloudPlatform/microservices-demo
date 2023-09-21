#!/bin/sh
# Check if sealights folder exists
if [ -d "/sealights/" ]; then
  /sealights/agent/SL.DotNet cdAgent --appName cartservice --branchName ${BRANCH} --buildName ${BUILD_NAME} \
         --binDir /app  --includeNamespace *.services* --target $1 --token ${SL_TOKEN} --workingDir /app \
         --identifyMethodsByFqn --labId ${SL_LAB_ID}
else
  dotnet $1
fi
