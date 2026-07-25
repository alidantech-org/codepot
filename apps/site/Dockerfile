# syntax=docker/dockerfile:1.7

FROM node:24-alpine AS builder

ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
ENV NEXT_TELEMETRY_DISABLED=1

ARG NEXT_PUBLIC_SITE_URL=https://code.alidantech.org
ENV NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL

WORKDIR /workspace

RUN corepack enable

COPY . .

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
    pnpm install --frozen-lockfile --filter @codepot/site...
RUN pnpm --filter @codepot/site validate:docs
RUN pnpm --filter @codepot/site build

# In a pnpm monorepo, Next.js standalone output preserves the workspace path.
# Fail the image build immediately if the expected production entrypoint is absent.
RUN test -f /workspace/apps/site/.next/standalone/apps/site/server.js

FROM node:24-alpine AS runner

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

WORKDIR /app

RUN addgroup --system --gid 1001 nodejs \
  && adduser --system --uid 1001 --ingroup nodejs nextjs

# Copy the complete standalone tree because it contains the traced monorepo
# dependencies at the root and the site server under apps/site.
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/site/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/site/.next/static ./apps/site/.next/static
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/site/public ./apps/site/public

WORKDIR /app/apps/site

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health >/dev/null || exit 1

CMD ["node", "server.js"]
