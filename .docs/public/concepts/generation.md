---
title: Generation
description: How Codepot resolves intent and templates into deterministic plans, rendered files, manifests, and reports.
order: 33
---

# Generation

Code generation is more than rendering a template string. Codepot treats it as an inspectable pipeline with explicit inputs, plans, file outcomes, and diagnostics.

## General pipeline

```text
load configuration
    ↓
load or compile semantic input
    ↓
load or compile template pack
    ↓
validate context and requirements
    ↓
resolve every output path
    ↓
plan dependencies and imports
    ↓
render virtual files
    ↓
classify writes and cleanup
    ↓
apply allowed changes
    ↓
report results
```

## Prototype generation

CodepotG derives a normalized context from OpenAPI and applies Jinja packs. It supports bundled languages, custom packs, dry runs, lifecycle policies, guarded refresh, commands, and reports.

## `codepotx` generation

`codepotx` compiles authoring and template artifacts, builds a complete `GenerationPlan`, renders every virtual file, and then applies managed writes and manifest cleanup.

Generation depends on authoring and templating ports rather than concrete engine classes, allowing memory adapters and alternate source providers.

## Determinism

A deterministic generator should produce the same plan and content from the same semantic inputs, template pack, variables, and configuration.

Stable digests and normalized artifacts make caching, comparisons, dry runs, and reviews possible.

## Reports

A useful result includes more than success or failure:

- planned paths;
- created, updated, unchanged, skipped, refused, and deleted files;
- diagnostics;
- commands;
- cleanup decisions;
- rollback information;
- durations and counts.

Every frontend should present the same underlying result according to its user experience.
