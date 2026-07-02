FROM node:22-alpine AS deps

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production && npm cache clean --force


FROM node:22-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

RUN npm run build


FROM node:22-alpine AS runner

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

RUN addgroup -g 1001 -S tsbl && \
    adduser -S -u 1001 -G tsbl tsbl

WORKDIR /app

COPY --from=builder --chown=tsbl:tsbl /app/public ./public
COPY --from=builder --chown=tsbl:tsbl /app/.next/standalone ./
COPY --from=builder --chown=tsbl:tsbl /app/.next/static ./.next/static

USER tsbl

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
