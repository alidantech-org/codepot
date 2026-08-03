---
title: Generation architecture
description: Understand source indexing, normalized contracts, template planning, rendering, lifecycle checks, and writes.
product: codepotg
package: codepotg
order: 3
---

# Generation architecture

CodepotG separates source loading, normalization, template planning, rendering, and project mutation.

## Pipeline

```text
Codepotg.yaml
    ↓ resolve task and paths
OpenAPI JSON/YAML
    ↓ indexed JSONL source cache
source resolvers
    ↓ inference and normalization
language-neutral contract graph
    ↓ language adapter
language-aware template context
    ↓ paths.yaml planner
selections, emissions, providers, barrels
    ↓ Jinja renderer
virtual output files
    ↓ lifecycle and safety policy
atomic writes, cleanup, commands, report
```

## Source layer

JSON input is streamed into a visible indexed JSONL cache. The cache allows later stages and lazy resolvers to retrieve records without retaining another complete decoded source tree.

YAML is a compatibility path. It must be parsed once, then CodepotG writes canonical JSON incrementally to `.codepotg/cache/.../source.json`. Unchanged YAML reuses the canonical conversion.

## Normalization layer

The inference pipeline builds stable views for:

- API information and servers;
- resources and operations;
- schemas and fields;
- parameters, bodies, responses, and media types;
- entities, relations, and constraints;
- access policies and runtime hooks;
- frontend screens and components;
- dependencies, diagnostics, extensions, and raw source data.

Known fields receive named normalized properties. Unknown extension values remain under `extensions`; original source objects remain under `raw`.

## Language adapter

The selected language adapter adds target-aware helpers for:

- type rendering;
- identifiers and naming;
- imports;
- literals;
- validation;
- files and comments;
- framework and package integration.

The normalized API contract remains language-neutral.

## Template planning

`paths.yaml` can use:

- legacy `folders` recipes;
- graph-based `selections` and `emissions`;
- explicit providers and provided facts;
- grouped emissions;
- barrels;
- lifecycle and write policy.

The graph planner bounds each template context to its declared selection and provider outputs instead of copying the entire source document into every render.

## Rendering

Jinja templates render into an in-memory result before project mutation. Output paths, dependency facts, imports, lifecycle mode, and diagnostics are known before a file is written.

## Mutation layer

The writer applies:

- managed-file updates;
- immutable-file create-once behavior;
- protected-root restrictions;
- safe stale cleanup;
- atomic writes;
- optional before and after commands.

A dry run stops before writes and commands.

## Reports and diagnostics

Each task result separates:

- planned files;
- written and updated files;
- unchanged files;
- immutable files created or skipped;
- refused unsafe writes;
- cleaned paths;
- warnings and informational diagnostics.

This separation lets a CLI, test, or future UI present the same generation facts without reimplementing the engine.