# ==========================================
# CloudTask Web - Multi-Stage Dockerfile
# Next.js 16 (Standalone Output) in Monorepo
# ==========================================

# 1. Base stage with pnpm
FROM node:22-alpine AS base
RUN corepack enable && corepack prepare pnpm@11.22.0 --activate
WORKDIR /app

# 2. Dependencies installation
FROM base AS deps
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json turbo.json ./
COPY apps/web/package.json ./apps/web/

RUN pnpm install --frozen-lockfile

# 3. Build stage
FROM deps AS builder
COPY apps/web ./apps/web

# Optional build arg for public API URL (defaults to relative /api behind ALB)
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Build Next.js application with standalone output
RUN pnpm --filter @cloudtask/web build

# 4. Production Runner stage
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy static assets and standalone bundle
COPY --from=builder /app/apps/web/public ./apps/web/public
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/static ./apps/web/.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "apps/web/server.js"]
