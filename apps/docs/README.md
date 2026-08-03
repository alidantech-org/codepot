# Codepot documentation source

This directory is the single source of truth for the public Codepot documentation site.

## Source layout

- `index.md` renders at `/docs`.
- `navigation.json` defines every published public path, recursive sidebar tree, package ownership, and compatibility redirect.
- `ecosystem.json` defines package and platform status, commands, registry links, and external links.
- `packages/index.md` renders at `/docs/packages`.
- `packages/<package>/index.md` renders at `/docs/packages/<package>`.
- Other nested Markdown files render at the matching path declared in `navigation.json`.

A source path and a public path may differ. The navigation record is authoritative:

```json
{
  "title": "Template variables",
  "path": "packages/codepotg/template-variables",
  "source": "packages/codepotg/template-variables"
}
```

## Package documentation

Every active package owns a complete nested tree rather than one oversized page:

```text
docs/packages/
├── codepot-openapi/
├── codepotg/
├── codepotx/
└── codepotx-cli/
```

Package roots must declare `package` in `navigation.json`. Descendants inherit that package identity and receive:

- a focused package sidebar;
- package status and registry information;
- package-scoped previous and next links;
- nested breadcrumbs;
- package-aware search ranking.

## Generated site data

`apps/site/scripts/sync-docs.mjs` precompiles:

- Markdown content;
- recursive navigation;
- page metadata and breadcrumbs;
- JSON tables of contents;
- page and heading search records;
- compatibility redirects;
- ecosystem metadata.

The runtime does not scan the repository or parse Markdown files. `prepare:docs` runs before development, type checking, linting, and production builds.

Do not edit files under `apps/site/src/generated/` manually.

## Validation rules

`apps/site/scripts/validate-docs.mjs` verifies:

- valid and unique public paths;
- valid source paths inside `docs/`;
- recursive child paths stay under their parent;
- every navigation source exists;
- frontmatter titles are present;
- package identities match;
- internal `/docs/...` links resolve or redirect;
- ecosystem products point to published documentation;
- available external links use HTTPS;
- unavailable links remain `null`.

## Commands

From the repository root:

```bash
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site sync:docs
pnpm --filter @codepot/site typecheck
pnpm --filter @codepot/site build
```

During local writing, run:

```bash
pnpm --filter @codepot/site dev
```

The `predev` script validates and synchronizes documentation automatically.
