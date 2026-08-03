---
title: Architecture
description: The three-tier Dryv architecture and its strict ownership boundaries.
---

# Architecture

```text
Authoring
    ↓
Canonical Dryv Runtime IR
    ↓
Templating
    ↓
Usage and generated output
```

## Authoring

Authoring defines software meaning, validates authored definitions, creates explicit relationships, and compiles into Runtime IR.

Authoring does not generate source code, select packs, define output paths, write files, serialize Runtime IR, or create a competing semantic model.

## Runtime

Runtime IR is the only semantic authority. The runtime owns canonical validation, serialization, loading, inspection, planning, plugin contracts, and safe generation orchestration.

Dryv is called a runtime because it executes the derivation process. It is not the runtime of the generated application.

## Templating

Packs define how Runtime IR becomes source code, configuration, documentation, packages, fragments, and projects. Packs use the same vocabulary and cannot redefine software meaning.

Templates own emitted characters. Target adapters provide target facts and validation rather than hidden rendering.

## Usage

Usage connects authored source or serialized IR, packs, options, project bindings, output destinations, and generation commands.

The CLI remains a frontend over runtime operations.

## Required properties

Generation must be deterministic, explainable, portable, inspectable, ownership-safe, and reproducible from locked inputs.
