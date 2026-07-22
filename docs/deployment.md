---
title: Deployment
description: Build and deploy the Codepot documentation site from the TypeScript monorepo.
order: 15
---

# Deployment

The active site lives at `apps/site` and uses Next.js standalone output.

## Local development

```bash
pnpm install
pnpm --filter @codepot/site dev
```

The app copies root `docs/` into an ignored generated directory before development and build. Root documentation remains the only maintained source.

## Production build

```bash
pnpm --filter @codepot/site build
pnpm --filter @codepot/site start
```

## Docker

Build from the repository root so pnpm workspace dependencies and shared docs are available:

```bash
docker build -f apps/site/Dockerfile -t codepot-site .
docker run --rm -p 3000:3000 codepot-site
```

The container exposes `/api/health` for readiness checks.

## Vercel

Create a Vercel project with repository root access and use `apps/site/vercel.json`. The configuration installs and builds from the workspace root while deploying the app output.

## Reverse proxy

When self-hosting, place a reverse proxy or load balancer in front of the standalone server, terminate TLS there, and forward traffic to port 3000. Cache immutable Next assets, but do not cache the health endpoint.

No GitHub Actions workflows are required or included.
