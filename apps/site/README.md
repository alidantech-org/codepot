# Codepot site

The active Codepot website is a preserved migration of `archives/site`. Its visual design, landing-section hierarchy, documentation shell, theme system, code blocks, navigation, and responsive behavior are intentionally reused rather than redesigned.

Root `docs/*.md` files are the only maintained documentation source. `scripts/sync-docs.mjs` embeds them into `src/generated/docs.ts` before development, type checking, or production builds.

## Local development

From the repository root:

```bash
corepack enable
pnpm install
pnpm dev:site
```

The site runs at `http://localhost:3000`.

## Type checking and build

```bash
pnpm --filter @codepot/site typecheck
pnpm --filter @codepot/site build
```

## Docker

Use the repository root as the build context because the site consumes root documentation and the workspace lockfile:

```bash
docker build -f apps/site/Dockerfile -t codepot-site .
docker run --rm -p 3000:3000 -e NEXT_PUBLIC_SITE_URL=http://localhost:3000 codepot-site
```

The container exposes `/health` for deployment probes.

## Vercel

Create a Vercel project with `apps/site` as the root directory. The included `vercel.json` installs dependencies from the monorepo root and builds the Next.js application.

Set:

```text
NEXT_PUBLIC_SITE_URL=https://your-domain.example
```
