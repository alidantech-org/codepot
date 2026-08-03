---
title: Release checklist
description: Validate packages, consumers, fixtures, site, and deployment before publishing.
order: 16
---

# Release checklist

Run from a clean checkout with Node 22.18+ and pnpm 11.15.1+.

```bash
pnpm install --frozen-lockfile
pnpm typecheck
pnpm test
pnpm build
pnpm check
```

## Package validation

- build `codepotx` and `codepotx-cli`;
- run Publint and Are The Types Wrong;
- inspect packed tarballs;
- verify every documented subpath import;
- verify no internal `@/*` aliases leak;
- verify Zod is not a peer dependency;
- install packed packages into temporary ESM consumers.

## Functional validation

- import-only migrated authoring fixture;
- local, package, Git, artifact, and memory sources;
- template-variable catalog and strict validation;
- deterministic plan and rendered artifact snapshots;
- managed, immutable, unchanged, stale, modified-stale, dry-run, cancellation, and rollback paths;
- CLI validate, inspect, variables, plan, and generate commands.

## Site validation

```bash
pnpm --filter @codepot/site typecheck
pnpm --filter @codepot/site build
pnpm --filter @codepot/site start
curl --fail http://localhost:3000/api/health
```

Also build the Docker image and verify the standalone container serves the home page, docs routes, static assets, and health endpoint.

Do not publish or close the shipping issue while any required check is unverified.
