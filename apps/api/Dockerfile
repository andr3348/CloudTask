# ==========================================
# CloudTask API - Multi-Stage Dockerfile
# Monorepo with pnpm and NestJS
# ==========================================

# 1. Base stage with pnpm enabled
FROM node:22-alpine AS base
RUN corepack enable && corepack prepare pnpm@11.22.0 --activate
WORKDIR /app

# 2. Dependencies installation
FROM base AS deps
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json turbo.json ./
COPY packages/db/package.json ./packages/db/
COPY apps/api/package.json ./apps/api/

RUN pnpm install --frozen-lockfile

# 3. Build stage
FROM deps AS builder
COPY packages/db ./packages/db
COPY apps/api ./apps/api

# Compile @cloudtask/db (runs prisma generate & tsc)
RUN pnpm --filter @cloudtask/db build

# Compile NestJS API
RUN pnpm --filter @cloudtask/api build

# 4. Production Runner stage
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3001

# Copy monorepo workspace dependencies and compiled files
COPY --from=builder /app/package.json /app/pnpm-workspace.yaml ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/packages/db ./packages/db
COPY --from=builder /app/apps/api/dist ./apps/api/dist
COPY --from=builder /app/apps/api/package.json ./apps/api/package.json
COPY --from=builder /app/apps/api/node_modules ./apps/api/node_modules

COPY apps/api/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

EXPOSE 3001

ENTRYPOINT ["./entrypoint.sh"]
