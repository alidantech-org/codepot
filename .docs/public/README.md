# Public documentation source

This directory contains the canonical Markdown and publication manifests consumed by the current documentation renderer in `apps/site`.

It is one section of the repository-wide `.docs` system, not a second documentation root.

## Contents

- `index.md` — `/docs` home page.
- `navigation.json` — public allowlist, hierarchy, source paths, package ownership, redirects, and ordering.
- `ecosystem.json` — active and frozen component metadata used by the site.
- `getting-started/` — current public project introduction.
- `dryv/` — public documentation for the active implementation.
- `packages/` — frozen package reference pages.
- `contributing/` — public repository and documentation rules.

Files that are not selected by `navigation.json` are not published, even when retained under this directory for historical reference.

## Current publication model

```text
.docs/public Markdown and manifests
        ↓
apps/site/scripts/validate-docs.mjs
        ↓
apps/site/scripts/sync-docs.mjs
        ↓
apps/site/src/generated/
        ↓
/docs routes
```

Generated files under `apps/site/src/generated/` are build artifacts and must not be edited manually.

## Validation

The validator checks:

- valid and unique public paths;
- source containment inside `.docs/public`;
- nested path relationships;
- source existence and frontmatter;
- package identity consistency;
- internal `/docs/...` links;
- redirects;
- ecosystem product IDs and documentation routes;
- external-link shape.

From the repository root:

```bash
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site sync:docs
pnpm --filter @codepot/site typecheck
pnpm --filter @codepot/site build
```

## Ownership rule

Public documentation may summarize the project for external users, but it must not redefine the canonical architecture, component status, task state, or agent rules. Link to the owning `.docs` section when deeper authority is required.
