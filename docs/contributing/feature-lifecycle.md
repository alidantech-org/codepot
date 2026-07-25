---
title: Feature lifecycle
description: How ideas move from mature prototypes into codepotx and later into the final Codepot language platform.
order: 61
---

# Feature lifecycle

Codepot uses a maturity pipeline rather than implementing every new idea directly in the final language.

## 1. Prototype and validate

New metadata, inference, template, and generation ideas can be implemented in `codepot-openapi` or `codepotg` and exercised in real projects.

Evidence should include:

- concrete use cases;
- input and output examples;
- compatibility expectations;
- failure behavior;
- safety implications;
- template and generator requirements;
- production feedback.

## 2. Stabilize in `codepotx`

Validated behavior is redesigned behind:

- explicit TypeScript contracts;
- JSON-safe artifacts;
- dependency-direction rules;
- frontend-neutral runtime operations;
- Node and memory platform adapters;
- deterministic planning and generation safety;
- focused tests.

The goal is semantic stability, not line-for-line copying of a prototype implementation.

## 3. Move mature semantics into the final platform

When the behavior is clear, it can inform:

- Codepot Lang syntax or standard-library constructs;
- semantic analysis rules;
- target-neutral IR;
- compiler or runtime traits;
- `codepot` CLI operations;
- LSP and editor capabilities;
- web and MCP interfaces.

## Release communication

Documentation must distinguish:

- available now;
- supported;
- active development;
- experimental;
- planned;
- TBD distribution links.

Do not describe a future migration or planned frontend as already released.
