---
title: Architecture
description: Autonomous engines, stable artifacts, dependency inversion, and replaceable frontends.
order: 3
---

# Architecture

```text
frontend (CLI, IDE, site, API)
              ↓
      Codepot runtime contract
              ↓
  ┌───────────┼───────────┐
  │           │           │
authoring  templating  generation
  │           │           │
  └──── stable contracts ─┘
              ↓
     injected platform ports
```

## Stable artifacts

The engines exchange versioned JSON-safe artifacts:

- `CompiledAuthoringArtifact`
- `CompiledTemplatePack`
- `TemplateVariableCatalog`
- `GenerationPlan`
- `RenderedGeneration`
- `GenerationManifest`

Artifacts contain no live Zod schemas, Handlebars programs, functions, mutable builders, maps, or service objects.

## Dependency direction

- Authoring does not import templating or generation.
- Templating consumes only stable authoring artifacts.
- Generation consumes authoring and templating through ports.
- Platform adapters implement filesystem, writer, codecs, source resolution, module loading, hashing, cache, commands, clock, IDs, and events.
- The runtime is the composition root.
- The CLI imports public package subpaths and contains no domain logic.

## Events

Events report stages, diagnostics, file classifications, commands, and runtime lifecycle. Required work always uses typed method calls and returned results. Listener failures are isolated and cannot change generation control flow.

## In-memory operation

Every engine can run against memory adapters. Programmatic generation may supply precompiled authoring and template artifacts, avoiding project source loading entirely.
