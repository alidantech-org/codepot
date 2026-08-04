# Practical implementation plan for Codepot

## Purpose

This plan is a language-neutral guide for a team implementing Codepot or a compatible Dryv runtime. It defines architecture, sequence, rules, evidence, and team practices without prescribing source language, framework, storage library, or template engine.

The plan assumes the governing architecture:

```text
Authoring source
    ↓
Author compiler
    ↓
Canonical Dryv Runtime IR
    ↓
Runtime validation, serialization, loading, and inspection
    ↓
Pack selection, binding, planning, and rendering
    ↓
Managed generated files and folders
```

The ownership rule is fixed:

```text
Authoring defines software.
Runtime owns canonical meaning.
Packs define code emission.
Usage connects IR, packs, and destinations.
Frontends call one reusable runtime.
```

## Documents

1. [`01-architecture-rules.md`](01-architecture-rules.md) — non-negotiable boundaries and invariants.
2. [`02-phased-implementation-plan.md`](02-phased-implementation-plan.md) — implementation sequence and exit criteria.
3. [`03-codepot-cookbook.md`](03-codepot-cookbook.md) — a practical recipe for crafting Codepot in any language.
4. [`04-validation-and-release.md`](04-validation-and-release.md) — evidence, conformance, and release gates.
5. [`05-governance-and-contribution.md`](05-governance-and-contribution.md) — team ownership, design changes, kernel growth, packs, and documentation truth.
6. [`06-reference-delivery-slice.md`](06-reference-delivery-slice.md) — the first complete product slice that should be proven.

## How a team should use this plan

### Before implementation

- agree on product scope and anti-goals;
- identify the normative architecture documents;
- assign ownership for kernel, authoring, planning, packs, output, and interfaces;
- select two real projects and one reference pack family;
- define baseline workflows for comparison;
- establish evidence and compatibility policies.

### During implementation

- complete phases in dependency order;
- keep public artifacts immutable and deterministic;
- add architecture tests before convenience features;
- use realistic fixtures from the start;
- record decisions and rejected alternatives;
- never bypass a boundary to make a demonstration faster;
- keep full deterministic generation as the correctness reference.

### Before expansion

Do not add more authoring languages, frameworks, marketplaces, visual tools, or aggressive incremental generation until the reference slice has passed its release gates and survived repeated real-project evolution.

## Definition of done

Codepot is not complete when it can render a template. The initial platform is complete when it can:

1. compile or load one canonical contract;
2. validate meaning and compatibility;
3. resolve and lock several packs;
4. calculate a complete artifact/dependency plan;
5. explain every selected and skipped derivation;
6. render deterministic output;
7. protect existing project files transactionally;
8. verify generated targets;
9. trace both directions between semantics and artifacts;
10. reproduce results on another supported machine;
11. expose the same operations to humans and AI agents;
12. demonstrate measurable benefit on real evolution tasks.

## Guiding philosophy

The architecture should make correct behavior easier than hidden behavior.

```text
Explicit meaning over inference.
Planning over mutation.
Composition over generated-file editing.
Compatibility evidence over assumptions.
Normal Git and toolchains over proprietary infrastructure.
One semantic contract over frontend-specific models.
Measured lifecycle value over generated line count.
```
