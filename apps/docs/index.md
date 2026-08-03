---
title: Codepot documentation
description: Learn Codepot from supported packages through the official JavaScript runtime and the final language platform.
---

# Codepot documentation

Codepot makes software intent explicit, reusable, and safe to generate. This documentation covers the supported OpenAPI and Jinja workflow, the official JavaScript runtime, and the final Rust language platform.

## Choose where to begin

### Build with supported packages

Use the current production-tested workflow when you need typed OpenAPI contracts and reusable Jinja generation today:

1. [Author contracts with codepot-openapi](/docs/packages/codepot-openapi/getting-started).
2. [Generate from OpenAPI with codepotg](/docs/packages/codepotg/getting-started).
3. [Learn how the prototype workflow fits together](/docs/prototype-workflow).

### Evaluate the official JavaScript runtime

Use the active workspace implementation when contributing to or testing the frontend-neutral rewrite:

1. [Understand codepotx](/docs/packages/codepotx).
2. [Compile typed authoring](/docs/packages/codepotx/authoring).
3. [Build and validate template packs](/docs/packages/codepotx/templating).
4. [Plan and execute generation](/docs/packages/codepotx/generation).
5. [Drive the runtime through codepotx-cli](/docs/packages/codepotx-cli).

### Explore the final platform

Read the platform documentation when working on the strongly typed language, compiler, CLI, LSP, extension, web tooling, or MCP integration:

- [Codepot Platform](/docs/codepot-platform)
- [Codepot Lang](/docs/codepot-lang)
- [Final codepot CLI](/docs/codepot-cli)
- [Codepot LSP](/docs/codepot-lsp)
- [Language extension](/docs/codepot-extension)

## Complete package documentation

Every active package has its own nested documentation tree and focused sidebar:

- [All packages](/docs/packages)
- [codepot-openapi](/docs/packages/codepot-openapi)
- [codepotg](/docs/packages/codepotg)
- [codepotx](/docs/packages/codepotx)
- [codepotx-cli](/docs/packages/codepotx-cli)

Package trees include getting started, architecture, configuration, complete feature explanations, template or API references, best practices, and troubleshooting.

## Understand the ecosystem

Codepot develops features through a deliberate maturity path:

```text
codepot-openapi + codepotg
        ↓ prove behavior in real projects
codepotx + codepotx-cli
        ↓ stabilize runtime and frontend contracts
Codepot Lang + compiler + codepot CLI + LSP + extension + web + MCP
```

Read [the ecosystem](/docs/ecosystem), [choose a workflow](/docs/choose-workflow), and [architecture](/docs/architecture) before deciding which layer belongs in a project.

## Documentation behavior

The website precompiles Markdown, nested navigation, breadcrumbs, tables of contents, and search records during `prepare:docs`. Runtime requests do not scan the repository or parse Markdown files.

Use the left sidebar to move between topics, the package-focused sidebar inside package docs, the sticky page table of contents on desktop, and search to open pages or exact headings.
