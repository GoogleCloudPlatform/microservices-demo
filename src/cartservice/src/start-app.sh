#!/bin/sh
# Check if sealights folder exists
if [ -d "/app/sealights/" ]; then
    /app/sealights/agent/SL.DotNet cdAgent --appName cartservice --branchName master --buildName cartservice1.1.3 \
                  --binDir /app --includeNamespace *icartservice.services*  --target $1 --tokenFile sltoken.txt  --workingDir /app \
                  --identifyMethodsByFqn --profilerLogLevel 7 --profilerLogDir /app/sealights/logs --labId integ_main_GoogleMicroserviceDemo
else
    dotnet $1
fi
