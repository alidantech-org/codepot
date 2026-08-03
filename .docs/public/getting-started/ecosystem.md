---
title: Codepot ecosystem
description: See how the supported prototypes, official JavaScript runtime, and final Rust platform complement one another.
order: 3
---

# Codepot ecosystem

Codepot is one project with several deliberately different implementation layers.

The packages should not be presented as accidental duplicates or immediate replacements. Each layer has a specific responsibility in how features are discovered, validated, stabilized, and eventually expressed in the final platform.

## Stage 1: mature working prototypes

### `codepot-openapi`

The first TypeScript contract engine for the project.

It provides typed builders for OpenAPI contracts, schemas, entities, relations, routes, access, runtime hooks, frontend metadata, and compiler-resolved `x-codegen` extensions.

### `codepotg`

The stable Python and Jinja generation runtime.

It consumes OpenAPI JSON or YAML, performs inference, builds normalized generator contexts, resolves dependencies and imports, and applies bundled or custom Jinja template packs.

### Why both remain supported

The prototype workflow is mature and has been exercised in real projects. It provides an important proving ground for new metadata, inference, templates, generation policies, and compatibility decisions.

```text
TypeScript contracts
    ↓ codepot-openapi
OpenAPI + x-codegen
    ↓ codepotg
normalized generator context
    ↓ Jinja template pack
generated project files
```

## Stage 2: official JavaScript ecosystem

### `codepotx`

`codepotx` is the official stable rewrite and long-term JavaScript release line.

It is not merely another OpenAPI CLI. It is a reusable runtime with explicit public artifacts and ports for authoring, templating, generation, platform services, and execution.

### `codepotx-cli`

`codepotx-cli` is a terminal frontend. It intentionally contains argument parsing, project-runtime discovery, event presentation, and exit-code handling—but not compiler or generator business logic.

```text
CLI       Web       Editor       MCP       Embedded API
  \        |           |           |            /
                  codepotx runtime
```

## Stage 3: final Codepot platform

The Rust-based platform places Codepot Lang at the center.

```text
Codepot Lang source
        ↓
lexer + parser + package graph + semantic analysis
        ↓
target-neutral IR and persistent workspace analysis
        ↓
codepot CLI | LSP | extension | web | MCP | generators
```

The final platform includes:

- [Codepot Lang](/docs/codepot-lang);
- [compiler and runtime](/docs/codepot-platform);
- the final [`codepot` CLI](/docs/codepot-cli);
- [Codepot LSP](/docs/codepot-lsp);
- [Codepot language extension](/docs/codepot-extension);
- planned [web and MCP tools](/docs/codepot-web-mcp).

## Feature movement

The normal direction is:

```text
codepot-openapi / codepotg
        ↓ proven behavior and production feedback
codepotx
        ↓ stabilized runtime contracts and frontend boundaries
Codepot Lang and final platform
```

Not every implementation detail moves unchanged. What moves forward is the validated semantic behavior: what a feature means, which inputs and outputs are stable, which safety guarantees matter, and how tools should consume it.

## Possible future consolidation

When `codepotx` reaches sufficient stability and feature coverage, it may replace more of the prototype workflow. That is a future migration decision, not the current status.

Until then:

- `codepot-openapi` and `codepotg` remain supported;
- `codepotx` remains the official stable rewrite in active development;
- Codepot Lang remains the final experimental platform direction.
