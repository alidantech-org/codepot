---
title: Migration strategy
description: Plan movement between supported prototypes, codepotx, and the final Codepot platform without treating active packages as already replaced.
order: 44
---

# Migration strategy

Migration in Codepot is capability-driven, not age-driven.

`codepot-openapi` and `codepotg` remain supported. `codepotx` is the official JavaScript rewrite in active development. Codepot Lang is the final experimental platform direction.

## Do not migrate only because a newer package exists

Before moving a real project, compare:

- authoring features;
- generated metadata;
- template capabilities;
- language adapters;
- custom filters and helpers;
- dependency and import behavior;
- lifecycle and cleanup policy;
- diagnostics and reports;
- public release and support status.

## Prototype to `codepotx`

A future migration may involve:

```text
codepot-openapi TypeScript contract
        ↓ adapt authoring imports and configuration
codepotx authoring artifact

CodepotG Jinja pack
        ↓ port templates and paths configuration
codepotx Handlebars pack

Codepotg.yaml
        ↓ map project-owned task settings
CodepotFile.yml
```

Jinja-to-Handlebars conversion is not a mechanical filename change. Filters, macros, context paths, grouping, imports, and lifecycle behavior must be compared against the target variable catalog and renderer.

## Runtime frontend migration

Terminal automation can move from `codepotg` or `codepot-openapi` commands to `codepotx-cli` only after equivalent runtime operations and outputs exist.

Applications that need a UI should integrate `codepotx/runtime` directly instead of parsing terminal output.

## `codepotx` to final platform

The final platform is not expected to preserve TypeScript implementation details unchanged.

Stable semantic concepts may move into:

- Codepot Lang constructs and standard-library definitions;
- compiler and IR contracts;
- runtime or generator traits;
- `codepot` CLI operations;
- LSP and editor features.

Migration tooling should be designed after the target semantics and compatibility boundary are stable.

## Recommended policy

1. Keep production projects on the supported workflow that meets their needs.
2. Test new capabilities in isolated projects or branches.
3. Record missing compatibility explicitly.
4. Migrate template packs only after variable and output parity is understood.
5. Keep generated output reviewable during the transition.
6. Do not remove prototype support before the replacement workflow is proven.
