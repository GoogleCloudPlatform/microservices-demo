#!/bin/sh
# Check if sealights folder exists
if [ -d "/app/sealights/" ]; then
    /app/sealights/agent/SL.DotNet cdAgent --appName cartservice --branchName main --buildName "0.4.1" --labId ${SL_LAB_ID} \
                  --binDir /app --includeNamespace *icartservice.services*  --target $1 --token ${SL_TOKEN}  --workingDir /app \
                  --identifyMethodsByFqn
else
    echo "there was an error"
fi