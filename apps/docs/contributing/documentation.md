---
title: Documentation guide
description: Maintain one accurate documentation source while keeping package trees, READMEs, navigation, search, and external links aligned.
order: 62
---

# Documentation guide

## Source of truth

All public documentation belongs under root `docs/`.

The active site must not maintain a second independent documentation copy inside `apps/site`. The site precompiles the root Markdown and metadata into generated artifacts.

## Before documenting a package

1. Read every active README and Markdown file owned by the package.
2. Read its package manifest or `pyproject.toml`.
3. Inspect public exports, configuration models, and CLI entrypoints.
4. Inspect examples and tests for supported behavior.
5. Compare every claim with implementation.
6. Mark unavailable or planned behavior clearly.
7. Exclude archives and superseded packages from current product claims.
8. Correct inaccurate package READMEs when the implementation proves them wrong.

## Recursive navigation

Add public pages to `docs/navigation.json` using `path`, `source`, and optional `children`:

```json
{
  "title": "codepotg",
  "path": "packages/codepotg",
  "source": "packages/codepotg/index",
  "package": "codepotg",
  "children": [
    {
      "title": "Template packs",
      "path": "packages/codepotg/template-packs",
      "source": "packages/codepotg/template-packs"
    }
  ]
}
```

- `path` is the public route after `/docs/`.
- `source` is the Markdown path relative to `docs/`, without `.md`.
- child paths must remain nested below their parent path;
- public paths and source files must be unique;
- package roots declare `package`; children inherit it;
- `docs/index.md` is configured separately as the optional catch-all root.

The site renders all pages through:

```text
apps/site/src/app/docs/[[...path]]/page.tsx
```

Do not create separate route implementations for package docs.

## Package documentation trees

A package should not be forced into one long page. Create a directory containing the complete learning path:

```text
docs/packages/example/
├── index.md
├── getting-started.md
├── architecture.md
├── configuration.md
├── workflows.md
├── reference.md
├── best-practices.md
└── troubleshooting.md
```

Add more focused reference pages when the package has complex APIs, template variables, configuration domains, or commands.

Package pages automatically receive:

- a focused package sidebar;
- collapsible nested navigation;
- package status and external links;
- package-scoped previous and next links;
- breadcrumbs;
- page and heading search records.

## Compatibility redirects

Use the `redirects` object in `navigation.json` when moving an important public page:

```json
{
  "redirects": {
    "codepotg": "packages/codepotg"
  }
}
```

Also add the corresponding Next.js redirect when the old URL must work before generated docs are loaded. Internal documentation should link directly to the new path after migration.

## Product metadata and links

Use `docs/ecosystem.json` for:

- product name and role;
- maturity stage;
- status and availability;
- documentation path;
- install command and CLI command;
- GitHub, npm, PyPI, marketplace, hosted, and future links.

Unavailable links must use:

```json
{
  "url": null,
  "status": "tbd"
}
```

The UI filters unavailable links rather than rendering broken buttons.

## Package frontmatter

Package identity may be declared in frontmatter and is inherited from package navigation:

```yaml
---
title: Template variables
description: Reference the values available to templates.
product: codepotg
---
```

Every page requires a title. New pages should also provide a clear description for metadata and search snippets.

## Generated artifacts

`sync-docs.mjs` creates:

- embedded Markdown content;
- recursive navigation;
- document metadata and breadcrumbs;
- `docs-toc.json`;
- page and heading search records;
- redirect metadata;
- ecosystem metadata.

Runtime requests do not scan the repository or parse Markdown.

## README policy

Package READMEs should remain concise entrypoints containing status, purpose, installation, core workflow, public links, and validation commands.

Detailed explanations belong in the root documentation site and should be linked from the README.

## Validation

```bash
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site sync:docs
pnpm --filter @codepot/site typecheck
pnpm --filter @codepot/site build
```

Validation checks recursive paths, sources, frontmatter, links, redirects, product IDs, and ecosystem link shape. Type checking and builds automatically regenerate the documentation artifacts first.
