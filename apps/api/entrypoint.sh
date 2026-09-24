#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
  echo "Applying database schema (prisma db push)..."
  /app/packages/db/node_modules/.bin/prisma db push --schema=/app/packages/db/prisma/schema.prisma --url="$DATABASE_URL" || echo "Warning: prisma db push failed or skipped."
fi

echo "Starting API on port ${PORT:-3001}..."
exec node dist/main.js