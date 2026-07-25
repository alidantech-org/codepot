---
title: Documentation guide
description: Maintain one accurate documentation source while keeping package READMEs, the landing page, navigation, and external links aligned.
order: 62
---

# Documentation guide

## Source of truth

All public documentation belongs under root `docs/`.

The active site must not maintain a second independent documentation copy inside `apps/site`.

## Before documenting a package

1. Read the package README.
2. Read its package manifest or `pyproject.toml`.
3. Inspect public exports and CLI entrypoints.
4. Inspect examples and tests for supported behavior.
5. Compare claims with implementation.
6. Mark unavailable or planned behavior clearly.
7. Exclude archived and superseded material from current product claims.

## Navigation

Add public pages to `docs/navigation.json`:

```json
{
  "title": "codepotx",
  "slug": "codepotx",
  "source": "packages/codepotx"
}
```

- `slug` is the public `/docs/<slug>` route.
- `source` is the Markdown path relative to `docs/`, without `.md`.
- slugs must be unique and use lowercase letters, digits, and hyphens.

## Product metadata and links

Use `docs/ecosystem.json` for:

- product name and role;
- maturity stage;
- status and availability;
- documentation slug;
- install command and CLI command;
- GitHub, npm, PyPI, marketplace, hosted, and future links.

Unavailable links must use:

```json
{
  "url": null,
  "status": "tbd"
}
```

The UI filters unavailable links.

## Package pages

Set `product` in frontmatter to render the shared status and external-link panel:

```yaml
---
title: codepotg
product: codepotg
---
```

## README policy

Package READMEs should remain concise entrypoints containing status, purpose, installation, core workflow, public links, and validation commands.

Detailed explanations belong in the root documentation site and should be linked from the README.

## Validation

```bash
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site build
```

Documentation validation checks navigation, nested sources, frontmatter, links, product IDs, documentation slugs, and ecosystem link shape.
