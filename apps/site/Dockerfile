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
# Fail the image build if the server, generated nested docs, or production docs
# routes are missing. This catches static-param and standalone regressions before
# a broken image can reach the reverse proxy.
RUN set -eux; \
    test -f /workspace/apps/site/.next/standalone/apps/site/server.js; \
    grep -q '"packages/codepotg"' /workspace/apps/site/src/generated/docs.ts; \
    mkdir -p /workspace/apps/site/.next/standalone/apps/site/.next; \
    cp -R /workspace/apps/site/.next/static /workspace/apps/site/.next/standalone/apps/site/.next/static; \
    cp -R /workspace/apps/site/public /workspace/apps/site/.next/standalone/apps/site/public; \
    cd /workspace/apps/site/.next/standalone/apps/site; \
    HOSTNAME=127.0.0.1 PORT=3000 node server.js >/tmp/codepot-site.log 2>&1 & \
    server_pid=$!; \
    trap 'kill "$server_pid" 2>/dev/null || true' EXIT; \
    ready=0; \
    for attempt in $(seq 1 30); do \
      if wget -qO- http://127.0.0.1:3000/health >/dev/null; then \
        ready=1; \
        break; \
      fi; \
      sleep 1; \
    done; \
    if [ "$ready" -ne 1 ]; then \
      cat /tmp/codepot-site.log; \
      exit 1; \
    fi; \
    wget -qO /tmp/docs-root.html http://127.0.0.1:3000/docs; \
    grep -q 'Codepot documentation' /tmp/docs-root.html; \
    wget -qO /tmp/docs-package.html http://127.0.0.1:3000/docs/packages/codepotg; \
    grep -qi 'codepotg' /tmp/docs-package.html; \
    kill "$server_pid"; \
    wait "$server_pid" || true; \
    trap - EXIT

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
