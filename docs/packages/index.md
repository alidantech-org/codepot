---
title: Codepot packages
description: Choose a Codepot package and follow its complete package-specific documentation.
order: 10
---

# Codepot packages

Codepot is built as a set of complementary packages with deliberately different responsibilities and maturity levels.

## Available packages

### Supported prototype workflow

- [`codepot-openapi`](/docs/packages/codepot-openapi) authors typed TypeScript contracts and emits OpenAPI 3.1 JSON or YAML with resolved `x-codegen` metadata.
- [`codepotg`](/docs/packages/codepotg) consumes OpenAPI and renders project-owned Jinja template packs into source code.

These packages are stable, supported, and useful in current projects.

### Official JavaScript runtime

- [`codepotx`](/docs/packages/codepotx) is the official frontend-neutral JavaScript runtime rewrite.
- [`codepotx-cli`](/docs/packages/codepotx-cli) is its deliberately thin terminal frontend.

These packages are implemented in the workspace and remain under active development before their first stable public release.

## How to choose

| Need | Package |
|---|---|
| Author typed OpenAPI contracts | `codepot-openapi` |
| Generate with Python and Jinja | `codepotg` |
| Embed the official TypeScript runtime | `codepotx` |
| Drive that runtime from a terminal | `codepotx-cli` |

For a cross-package comparison, read [Choose a workflow](/docs/choose-workflow).

## Documentation policy

Each package tree contains:

- a package overview and learning path;
- installation and first-project guidance;
- architecture and core concepts;
- complete configuration and command references;
- examples, best practices, and troubleshooting;
- clear release-status notes.

The documentation is compiled from Markdown during the site build. Package READMEs, source exports, configuration models, examples, and tests remain the factual source for package behavior.