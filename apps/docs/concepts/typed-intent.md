---
title: Typed software intent
description: Why Codepot treats software meaning as reusable source material rather than rediscovering it from generated code.
order: 30
---

# Typed software intent

Software intent is the meaning behind an application: resources, values, schemas, operations, relationships, access, lifecycle rules, screens, workflows, and implementation constraints.

In ordinary projects that meaning is scattered across source code, decorators, database definitions, API documents, prompts, comments, tickets, and team knowledge.

Codepot makes it explicit so that several tools can consume the same reviewed source.

## Why typing matters

Typed intent can be validated before files are generated.

A compiler or contract engine can detect:

- unknown references;
- incompatible projections;
- invalid function arguments;
- impossible relationships;
- unsafe public fields;
- missing template variables;
- duplicate output paths;
- unresolved dependencies.

A prose prompt alone cannot provide the same deterministic contract.

## What changes across generations

### `codepot-openapi`

TypeScript builders compile to OpenAPI and `x-codegen` metadata.

### `codepotg`

OpenAPI is inferred into normalized Python generation contracts consumed by Jinja packs.

### `codepotx`

Typed authoring compiles to stable JSON-safe artifacts consumed by templating, generation, and runtime operations.

### Codepot Lang

A purpose-built strongly typed language compiles to target-neutral semantic IR and persistent workspace analysis.

## What remains constant

- Intent is authored before output.
- References are resolved centrally.
- Templates should receive resolved meaning instead of guessing it.
- Multiple frontends should use the same artifacts.
- Generated code is an output, not the only place where project meaning exists.

## Why AI benefits

AI agents can read or query a structured project model instead of repeatedly rediscovering architecture from a large repository.

That can reduce prompt repetition, naming drift, unsafe assumptions, and inconsistent boilerplate while keeping reviewed contracts and templates under developer ownership.
