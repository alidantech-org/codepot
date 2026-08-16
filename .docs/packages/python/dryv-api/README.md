# dryv-api

Code: `packages/python/dryv-api`

Status: active refactor after Dryv Runtime boundary cleanup.

Before changing production code, read:

1. [`../dryv/ARCHITECTURE.md`](../dryv/ARCHITECTURE.md).
2. [`../dryv/IMPLEMENTATION-RULES.md`](../dryv/IMPLEMENTATION-RULES.md).
3. the exact active task under [`tasks/`](tasks/).
4. [`.docs/TODO.md`](../../../TODO.md).

## Purpose

`dryv-api` is the execution and transport coordinator around Dryv Runtime.

```text
Project Client
    ↓ dryv.yaml + Canonical IR + pack bundles
  dryv-api
    ↓ normalized RuntimeInput
Dryv Runtime
    ↓ GenerationPlan
  dryv-api
    ↓ template/context preflight + bounded render scheduling
Render Clients
    ↓ generated artifacts
  dryv-api
    ├── stream artifacts
    └── deterministic bundle
        ↓
Project Client
    ↓ diff / apply
user filesystem
```

The API owns:

- build sessions and cancellation;
- logical resource upload/normalization;
- HTTP build lifecycle;
- WebSocket build progress/control;
- Render Client registration and capability inventory;
- template/context preflight;
- renderer capacity and bounded scheduling;
- backpressure and artifact streaming;
- deterministic bundle creation and download metadata.

The API does not own:

- Canonical IR meaning;
- `dryv.yaml` semantics;
- pack semantics or selection;
- context construction;
- planned output paths;
- author implementation execution;
- template-language implementation;
- local project diff/apply/filesystem writes.

Renderer requirements come from `GenerationPlan`. `dryv-api` must not independently parse pack rules to create a competing plan.

The old Author Backend/session and subprocess/stdio API task design is superseded and must not be retained through compatibility code.

Initial implementation may be stateless. Stateful account/project content-addressed reuse and MCP exposure are future extensions and are out of scope unless explicitly approved.

Do not add tests during the current production-code implementation phase. Test work begins only after explicit user approval of the final production structure and code.
