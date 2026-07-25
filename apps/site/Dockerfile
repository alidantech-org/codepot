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

# The package postbuild step prepares one complete standalone artifact for both
# local `npm start` and Docker. Fail the image build unless the server, static
# assets, generated nested docs, and representative production routes work.
RUN set -eux; \
    test -f /workspace/apps/site/.next/standalone/apps/site/server.js; \
    test -d /workspace/apps/site/.next/standalone/apps/site/.next/static; \
    test -d /workspace/apps/site/.next/standalone/apps/site/public; \
    grep -q '"packages/codepotg"' /workspace/apps/site/src/generated/docs.ts; \
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

# The complete postbuild-prepared standalone tree includes traced dependencies,
# the monorepo server entrypoint, public files, and Next.js static assets.
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/site/.next/standalone ./

WORKDIR /app/apps/site

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health >/dev/null || exit 1

CMD ["node", "server.js"]
