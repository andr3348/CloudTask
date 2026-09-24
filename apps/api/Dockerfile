# ---- base ----
FROM node:22-alpine AS base
RUN apk add --no-cache openssl libc6-compat
RUN npm install -g pnpm@11.22.0
WORKDIR /app

# ---- builder ----
FROM base AS builder
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json turbo.json ./
COPY apps ./apps
COPY packages ./packages
RUN pnpm install --frozen-lockfile
RUN pnpm --filter @cloudtask/db build
RUN pnpm --filter @cloudtask/api build

# ---- runner ----
FROM base AS runner
ENV NODE_ENV=production
ENV PORT=3001
WORKDIR /app

COPY --from=builder /app/package.json /app/pnpm-workspace.yaml ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/packages ./packages
COPY --from=builder /app/apps/api/dist ./apps/api/dist
COPY --from=builder /app/apps/api/package.json ./apps/api/package.json
COPY --from=builder /app/apps/api/node_modules ./apps/api/node_modules
COPY apps/api/entrypoint.sh ./apps/api/entrypoint.sh
RUN chmod +x ./apps/api/entrypoint.sh

WORKDIR /app/apps/api
EXPOSE 3001

CMD ["sh", "entrypoint.sh"]
