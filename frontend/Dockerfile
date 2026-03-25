# ── Stage 1: Install dependencies ─────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ── Stage 2: Build the Next.js app ───────────────────────────────────────────
FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build-time env vars (NEXT_PUBLIC_* are baked into the client bundle)
ARG NEXT_PUBLIC_APP_URL=http://localhost:3000
ARG NEXT_PUBLIC_CB_IMAGE_PREFIX=https://beta-images.codebasics.io/filters:format(webp)/fit-in/50x50
ENV NEXT_PUBLIC_APP_URL=$NEXT_PUBLIC_APP_URL
ENV NEXT_PUBLIC_CB_IMAGE_PREFIX=$NEXT_PUBLIC_CB_IMAGE_PREFIX

# Auth.js requires these to be present at module-load time during build
ARG AUTH_SECRET
ARG AUTH_CODEBASICS_ID
ARG AUTH_CODEBASICS_SECRET
ARG CODEBASICS_BASE_URL=https://beta.codebasics.io
ENV AUTH_SECRET=$AUTH_SECRET
ENV AUTH_CODEBASICS_ID=$AUTH_CODEBASICS_ID
ENV AUTH_CODEBASICS_SECRET=$AUTH_CODEBASICS_SECRET
ENV CODEBASICS_BASE_URL=$CODEBASICS_BASE_URL

ENV NODE_OPTIONS="--max-old-space-size=2048"

RUN npm run build

# ── Stage 3: Production runner ────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone output + static assets
COPY --from=build /app/public ./public
COPY --from=build --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=build --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
