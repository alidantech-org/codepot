---
title: Code generation
description: Deterministic planning, in-memory rendering, transactional writes, manifests, imports, and reports.
order: 10
---

# Code generation

Generation is an orchestrator over stable authoring and template artifacts.

```text
load CodepotFile.yml
        ↓
run required before commands
        ↓
compile or load authoring artifact
        ↓
compile or load template pack
        ↓
validate template context
        ↓
plan outputs and dependency imports
        ↓
render all files in memory
        ↓
apply one reversible managed write
        ↓
run after commands
        ↓
commit transaction and report
```

## Planning

The planner resolves all output paths before dependencies. It then builds a semantic output index and lets an injected import adapter map references to generated files.

Duplicate output paths, ambiguous dependency targets, unsafe paths, invalid selectors, and unknown template variables fail before rendering.

## Rendering

Rendering is deterministic and cacheable by plan/template digests. No generated file is written until every template has rendered successfully.

## Writing

The changed-aware writer classifies files as created, updated, unchanged, skipped, or refused. A task manifest additionally records deleted and rolled-back files.

## Reports

Each successful task returns its plan, rendered artifact, manifest, commands, file outcomes, cleaned paths, diagnostics, and a `GenerationReport` with counts and operational duration.
