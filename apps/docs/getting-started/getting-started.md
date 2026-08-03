---
title: Getting started
description: Start with the supported prototype workflow today or evaluate the official codepotx rewrite from the workspace.
order: 2
---

# Getting started

There are two practical starting points. Choose according to whether you need the most mature production-used workflow or want to evaluate the official JavaScript rewrite.

## Path A: supported OpenAPI and Jinja workflow

Use this path when you need a mature generator that has already been used in real projects.

### 1. Install the packages

```bash
npm install codepot-openapi zod
python -m pip install codepotg
```

### 2. Author and emit OpenAPI

Create a TypeScript contract using `codepot-openapi`, then generate JSON or YAML:

```bash
npx codepot-openapi generate
```

The output is a standard OpenAPI document. Optional `x-codegen` metadata carries additional information about resources, entities, access, hooks, frontends, and operation roles.

### 3. Configure CodepotG

Create `Codepotg.yaml` in the consuming project:

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    output: ./generated/sdk
```

### 4. Preview and generate

```bash
codepotg generate sdk --dry-run --verbose
codepotg generate sdk
```

Read the full [prototype workflow guide](/docs/prototype-workflow) for custom Jinja packs, lifecycle policy, and safe cleanup.

## Path B: official `codepotx` rewrite

Use this path when contributing to or evaluating the frontend-neutral JavaScript runtime being prepared as the official stable release.

The packages are currently developed in this workspace:

```bash
corepack enable
pnpm install
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
```

A consumer combines:

```text
codepotx.config.ts
        +
Handlebars template pack with paths.yaml
        +
CodepotFile.yml
        ↓
codepotx runtime
        ↓
plan, render, safe write, manifest, diagnostics
```

The CLI frontend exposes the `codepotx` command:

```bash
codepotx validate
codepotx variables sdk
codepotx plan sdk --json
codepotx generate sdk --dry-run
codepotx generate sdk
```

Read the [codepotx workflow guide](/docs/codepotx-workflow) for the complete model.

## Exploring the final platform

The Rust project is developed in the separate `codepot_lang` repository. From a local clone:

```bash
cargo build --workspace
cargo test --workspace
cargo run -p codepot-cli -- check
cargo run -p codepot-cli -- compile
cargo run -p codepot-cli -- lsp --stdio
```

The final CLI command is:

```bash
codepot
```

Read [Codepot Lang](/docs/codepot-lang), [codepot CLI](/docs/codepot-cli), [Codepot LSP](/docs/codepot-lsp), and [Language extension](/docs/codepot-extension) before treating experimental features as release commitments.

## Next steps

- [Choose a workflow](/docs/choose-workflow)
- [Package links](/docs/package-links)
- [Architecture](/docs/architecture)
- [Feature lifecycle](/docs/feature-lifecycle)
