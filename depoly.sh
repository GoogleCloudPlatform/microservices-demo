#!/bin/sh

# Fist generate code context for the cloud debugger
gcloud debug source gen-repo-info-file
for module in src/*; do
    cp source-context.json "$module"
done

# Now deploy on GKE
skaffold run
