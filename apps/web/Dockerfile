# ---- base ----
FROM node:22-alpine AS base
RUN apk add --no-cache libc6-compat
RUN npm install -g pnpm@11.22.0
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app

# ---- builder ----
FROM base AS builder
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json turbo.json ./
COPY apps ./apps
COPY packages ./packages
RUN pnpm install --frozen-lockfile
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN pnpm --filter @cloudtask/web build

# ---- runner ----
FROM base AS runner
ENV NODE_ENV=production
ENV PORT=3000
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/packages ./packages
COPY --from=builder /app/apps/web/node_modules ./apps/web/node_modules
COPY --from=builder /app/apps/web/.next ./apps/web/.next
COPY --from=builder /app/apps/web/public ./apps/web/public
COPY --from=builder /app/apps/web/package.json ./apps/web/package.json
COPY --from=builder /app/apps/web/next.config.ts ./apps/web/next.config.ts
WORKDIR /app/apps/web
EXPOSE 3000
CMD ["node", "node_modules/next/dist/bin/next", "start", "-p", "3000"]
