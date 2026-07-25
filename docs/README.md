# Codepot documentation source

This directory is the single source of truth for the public Codepot documentation site.

- `index.md` is the documentation-source entry point.
- `navigation.json` defines published pages and learning order.
- `ecosystem.json` defines package and platform status, commands, and external links.
- Nested Markdown folders contain the public documentation rendered under `/docs`.

Validate and build from the repository root:

```bash
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site build
```
