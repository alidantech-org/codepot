---
title: Repository structure
description: Understand the active Codepot monorepo areas and the separate Codepot Lang repository.
order: 60
---

# Repository structure

## Active monorepo

```text
apps/site
  Codepot website and Markdown documentation renderer

docs
  single source of truth for public documentation, navigation, and ecosystem links

packages/nodejs/codepot-openapi
  supported TypeScript OpenAPI prototype

packages/python/codepotg
  supported Python and Jinja generator

packages/nodejs/codepotx
  official frontend-neutral JavaScript runtime rewrite

packages/nodejs/codepotx-cli
  thin CLI frontend for codepotx
```

Anything under `archives/` is excluded from active documentation audits and public site composition.

## Separate Rust repository

```text
alidantech-org/codepot_lang
├── crates/
├── stdlib/std/
└── vcode/
```

That repository contains Codepot Lang, compiler and analysis crates, target-neutral IR, CLI, LSP, formatter, standard library, and the VS Code extension.

## Documentation ownership

All public site Markdown lives under root `docs/` in the monorepo.

`docs/navigation.json` controls which files are published and their learning order. Each item uses a public flat `slug` and may point to a nested Markdown `source`.

`docs/ecosystem.json` is the central product and external-link configuration.

The site build validates and embeds these files into `apps/site/src/generated/docs.ts`.
