# Codepot site

The active Codepot website preserves the established site design while using the current brown Codepot brand, responsive landing sections, interactive examples, and a fully precompiled documentation system.

## Documentation architecture

Root `docs/` is the maintained documentation source. The site does not keep a second independent Markdown copy.

All public documentation is rendered by one optional catch-all route:

```text
src/app/docs/[[...path]]/page.tsx
```

It serves:

```text
/docs
/docs/getting-started
/docs/packages
/docs/packages/codepot-openapi/...
/docs/packages/codepotg/...
/docs/packages/codepotx/...
/docs/packages/codepotx-cli/...
```

`docs/navigation.json` is the recursive public allowlist. It defines:

- public paths;
- Markdown source paths;
- nested children;
- package ownership;
- compatibility redirects;
- sidebar order.

Package routes automatically use focused package navigation. General routes use the global documentation sidebar.

## Generated artifacts

`scripts/validate-docs.mjs` verifies recursive paths, sources, frontmatter, internal links, redirects, product IDs, and ecosystem links.

`scripts/sync-docs.mjs` precompiles:

- Markdown content;
- recursive navigation;
- breadcrumbs;
- JSON tables of contents;
- page and heading search records;
- redirects;
- ecosystem metadata.

Generated outputs live under `src/generated/` and must not be edited manually. The runtime does not scan Markdown files.

`prepare:docs` runs before development, type checking, linting, and production builds.

## Local development

From the repository root:

```bash
corepack enable
pnpm install
pnpm --filter @codepot/site dev
```

The site runs at `http://localhost:3000` by default.

## Documentation validation

```bash
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site sync:docs
```

## Type checking and build

```bash
pnpm --filter @codepot/site typecheck
pnpm --filter @codepot/site build
```

A direct TypeScript check is also supported after dependencies are installed:

```bash
cd apps/site
tsc6 --noEmit
```

## Docker

Use the repository root as the build context because the site consumes root documentation and the workspace lockfile:

```bash
docker compose build --pull site
docker compose up -d site
```

The production mapping is:

```text
https://code.alidantech.org
        ↓
http://127.0.0.1:3020
        ↓
container port 3000
```

The container exposes `/health` for deployment probes. See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for the complete process.

## Deployment URL

Set:

```text
NEXT_PUBLIC_SITE_URL=https://code.alidantech.org
```

This value controls canonical metadata, Open Graph URLs, robots, and sitemap output.
