#!/bin/sh
set -e

# Sync database schema with PostgreSQL if DATABASE_URL is configured
if [ -n "$DATABASE_URL" ]; then
  echo "Syncing database schema with Prisma (prisma db push)..."
  npx prisma db push --schema=./packages/db/prisma/schema.prisma --skip-generate || echo "Warning: prisma db push failed or skipped."
fi

echo "Starting CloudTask API on port ${PORT:-3001}..."
exec node apps/api/dist/main.js
