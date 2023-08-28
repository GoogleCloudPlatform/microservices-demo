#!/bin/sh
# Check if sealights folder exists
if [ -d "/app/sealights/" ]; then
    /app/sealights/agent/SL.DotNet cdAgent --appName cartservice --branchName master --buildName 0.1 \
                  --binDir /app --includeNamespace *icartservice.services*  --target $1 --token ${SL_TOKEN}  --workingDir /app \
                  --identifyMethodsByFqn --profilerLogLevel 7 --profilerLogDir /app/sealights/logs --labId ${SL_LAB_ID}
else
    dotnet $1
fi
