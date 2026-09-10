#!/bin/sh
set -e
echo "Applying database schema (prisma db push)..."
/app/packages/db/node_modules/.bin/prisma db push --schema=/app/packages/db/prisma/schema.prisma --url="$DATABASE_URL"
echo "Starting API..."
exec node dist/main.js
