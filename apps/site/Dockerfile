FROM node:24-alpine AS builder

ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /workspace

RUN corepack enable

COPY . .
RUN pnpm install --frozen-lockfile
RUN pnpm --filter @codepot/site build

FROM node:24-alpine AS runner

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

WORKDIR /app

RUN addgroup --system --gid 1001 nodejs \
  && adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /workspace/apps/site/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/site/.next/static ./apps/site/.next/static
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/site/public ./apps/site/public

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health >/dev/null || exit 1

CMD ["node", "apps/site/server.js"]
