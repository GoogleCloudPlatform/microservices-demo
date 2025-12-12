#!/bin/sh
set -e

# Run prisma migrations
npx prisma migrate deploy --config=/app/dist/prisma.config.js

if [ "$NODE_ENV" = "development" ] || [ "$DEBUG" = "true" ]; then
  echo "Starting in DEBUG mode..."
  exec node --inspect=0.0.0.0:9229 dist/index.js
else
  echo "Starting in PRODUCTION mode..."
  exec node dist/index.js
fi
