#!/bin/sh
# Check if sealights folder exists
mkdir -p /app/sealights/logs
mkdir -p /app/sealights/agent
wget -nv -O sealights-dotnet-agent-alpine.tar.gz ${AGENT_URL}

tar -xzf ./sealights-dotnet-agent-alpine.tar.gz --directory /app/sealights/agent
chmod -R 777 /app/sealights

if [ -d "/app/sealights/" ]; then
  /app/sealights/agent/SL.DotNet cdAgent --appName cartservice --branchName main --buildName ${BUILD_NAME} \
         --binDir /app  --includeNamespace *.services* --target $1 --token ${SL_TOKEN} --workingDir /app \
         --identifyMethodsByFqn --labId ${SL_LAB_ID}
else
  dotnet $1
fi
