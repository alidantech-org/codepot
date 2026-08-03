# Codepot site

**Status:** Active

This is the public Codepot website and the current renderer for Codepot documentation.

Canonical authored documentation lives under [`.docs`](../../.docs/README.md). Public pages are selected from [`.docs/public`](../../.docs/public/README.md); the site does not maintain a second Markdown copy.

## Responsibilities

- render the project and marketing website;
- validate and precompile selected public documentation;
- provide documentation navigation, search, redirects, and tables of contents;
- build the standalone production application;
- expose the deployment health endpoint.

The long-term dedicated documentation application boundary is [`apps/docs`](../docs/README.md). Moving rendering responsibility there requires an approved task and must not duplicate documentation sources.

## Local development

From the repository root:

```bash
corepack enable
pnpm install
pnpm --filter @codepot/site dev
```

## Validation and build

```bash
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site sync:docs
pnpm --filter @codepot/site typecheck
pnpm --filter @codepot/site build
```

Generated documentation files under `src/generated/` are build artifacts and must not be edited manually.

## Canonical documentation

- [Application architecture](../../.docs/apps/site/README.md)
- [Deployment](../../.docs/apps/site/deployment.md)
- [Public documentation source](../../.docs/public/README.md)
- [Documentation ownership rules](../../.docs/agents/rules/documentation.md)
