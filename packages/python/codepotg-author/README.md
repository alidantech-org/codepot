# codepotg-author

`codepotg-author` is the typed Python authoring compiler for CodepotG v2.

It lets authors define contracts, groups, reusable properties, structural schemas, schema projections, field behavior hints, operations, known facets, storage mappings, policies, events, value sources, views, parts, workflows, presentations, guidance, and namespaced tags through a concise Python API. The package compiles those declarations into the same closed, immutable `codepotg.ir.Contract` consumed by the rest of CodepotG.

## Core promise

```text
concise typed Python authoring
        ↓
typed refs + multi-pass author compiler
        ↓
closed neutral Codepot IR
        ↓
canonical JSON/YAML for debugging and transport
        ↓
root-first planning, packs, templates, adapters, and writers
```

The authoring layer may be expressive and composable. The compiled IR remains finite, rigid, deterministic, portable, selector-safe, and oblivious to framework/runtime implementation details.

## Non-goals

This package does not:

- create a second semantic graph;
- replace or extend the CodepotG kernel;
- parse OpenAPI;
- select templates or output paths;
- render target-language syntax;
- write project files;
- execute commands;
- model PostgreSQL, MongoDB, Prisma, React, Flutter, NestJS, FastAPI, or other runtime/framework APIs;
- expose Pydantic models, Python callables, mutable registries, or authoring builders to templates;
- use process-global decorator or reference registries.

## Status

The package currently contains the approved architecture, complete implementation task ledger, parallel work rules, implementation prompt, and empty mirrored project structure. Runtime implementation has not started.

Start with:

- [`docs/IDEA.md`](docs/IDEA.md)
- [`docs/README.md`](docs/README.md)
- [`docs/design/00-authoring-architecture.md`](docs/design/00-authoring-architecture.md)
- [`docs/tasks/00-master-plan.md`](docs/tasks/00-master-plan.md)
- [`docs/prompts/IMPLEMENTATION_PROMPT.md`](docs/prompts/IMPLEMENTATION_PROMPT.md)
