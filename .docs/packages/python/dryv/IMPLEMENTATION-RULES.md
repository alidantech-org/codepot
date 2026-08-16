# Dryv implementation rules

Status: mandatory for the current Dryv Engine and `dryv-api` refactor.

These rules enforce the approved architecture in [`ARCHITECTURE.md`](ARCHITECTURE.md). They are implementation constraints, not suggestions.

## Branch

- Work only on the existing `develop` branch.
- Never create another branch.

## Approval and test gate

- Production architecture and production code are implemented first.
- Do not create, modify, rewrite or expand tests during the current implementation phase.
- Do not keep old architecture alive merely to satisfy existing tests.
- Existing tests may be inspected as historical evidence, but they are not allowed to force compatibility with superseded contracts.
- New test design begins only after the user explicitly approves the final production file/folder structure and production code.
- Do not add temporary test-only adapters, fixtures, aliases or compatibility entry points.

## No compatibility shims

The superseded AuthorSession/RenderSession-in-Runtime architecture is deleted, not deprecated.

Forbidden:

- compatibility aliases;
- deprecated facade classes;
- old-to-new adapter layers whose only purpose is preserving removed APIs;
- duplicate Runtime entry points;
- re-exporting deleted contracts under old names;
- old subprocess/stdio paths retained as alternate execution paths;
- comments such as "temporary compatibility" followed by production compatibility code.

If old production code conflicts with the approved architecture, remove it.

## Small-file rule

Production source files must stay small and single-purpose.

- Target substantially below 500 lines.
- 500 lines is the hard maximum for a production source file in this refactor unless the user explicitly approves an exception first.
- If a file approaches 500 lines, split it by an existing architectural responsibility, not by inventing generic buckets.
- Do not create `common`, `shared`, `utils`, `helpers`, `misc`, `base`, `core_helpers`, or similar dumping-ground modules/directories.
- Prefer direct names such as `selection.py`, `context.py`, `registry.py`, `scheduler.py`, `streaming.py` and `manifest.py`.
- Avoid unnecessary manager/service/factory layers. A layer exists only when it owns a real responsibility named in the architecture.
- Keep functions direct, typed and explicit. Avoid speculative abstraction.

## One owner per concern

Every concept has exactly one architectural owner.

| Concern | Owner |
|---|---|
| Canonical software meaning | `dryv.ir` |
| `dryv.yaml` semantics | Dryv Engine Project Feature |
| Canonical IR representation | Serialization Feature |
| Logical build resources | Resources Feature / API resource transport |
| Pack semantics | Packs Feature |
| Pack selection | Planning Feature |
| Context construction | Planning Feature |
| Semantic/generation dependency graph | Planning Feature |
| Planned artifact paths | Planning Feature / Runtime contracts |
| Runtime progress | Runtime events |
| Renderer discovery/capacity | `dryv-api` |
| Template syntax/context preflight | Render Client coordinated by `dryv-api` |
| Template execution | Render Client |
| Renderer scheduling/backpressure | `dryv-api` |
| Generated artifact byte transport | `dryv-api` |
| ZIP/bundle creation | `dryv-api` |
| Diff/apply/filesystem writes | Project Client |
| Shell/Git commands | Project Client or agent |

Do not duplicate a concept in a second package for convenience.

## Required final Dryv Engine tree

The active production package must converge to this ownership shape:

```text
packages/python/dryv/
├── pyproject.toml
├── README.md
└── src/
    └── dryv/
        ├── __init__.py
        ├── py.typed
        ├── ir/
        │   └── canonical IR model modules
        ├── features/
        │   ├── __init__.py
        │   ├── serialization/
        │   │   ├── __init__.py
        │   │   ├── decode.py
        │   │   └── encode.py
        │   ├── project/
        │   │   ├── __init__.py
        │   │   ├── contracts.py
        │   │   └── loader.py
        │   ├── resources/
        │   │   ├── __init__.py
        │   │   ├── contracts.py
        │   │   └── registry.py
        │   ├── hashing/
        │   │   ├── __init__.py
        │   │   └── hashing.py
        │   ├── ir/
        │   │   ├── __init__.py
        │   │   ├── validation.py
        │   │   ├── indexing.py
        │   │   └── resolution.py
        │   ├── packs/
        │   │   ├── __init__.py
        │   │   ├── contracts.py
        │   │   ├── loader.py
        │   │   └── validation.py
        │   ├── planning/
        │   │   ├── __init__.py
        │   │   ├── contracts.py
        │   │   ├── selection.py
        │   │   ├── context.py
        │   │   └── planner.py
        │   ├── cache/
        │   │   ├── __init__.py
        │   │   └── cache.py
        │   └── diagnostics/
        │       ├── __init__.py
        │       └── diagnostics.py
        ├── runtime/
        │   ├── __init__.py
        │   ├── contracts.py
        │   ├── events.py
        │   └── runtime.py
        └── versions/
            └── __init__.py
```

Canonical IR may keep multiple clearly named model modules under `dryv/ir/`; do not collapse that semantic model merely to reduce file count.

The following old Engine owners must not remain as active production architecture:

```text
dryv/api/
dryv/config/
dryv/domain/
dryv/testing/
dryv/runtime/engine.py
dryv/runtime/facade.py
dryv/features/authoring/
dryv/features/templating/
dryv/features/scheduling/
dryv/features/artifacts/
```

Any remaining top-level legacy package is audited: if it duplicates or wraps an approved owner, delete it rather than keeping a forwarding shim.

## Required final dryv-api tree

```text
packages/python/dryv-api/
├── pyproject.toml
├── README.md
└── src/
    └── dryv_api/
        ├── __init__.py
        ├── py.typed
        ├── server.py
        ├── contracts.py
        ├── builds/
        │   ├── __init__.py
        │   ├── session.py
        │   ├── manager.py
        │   └── events.py
        ├── resources/
        │   ├── __init__.py
        │   ├── bundle.py
        │   └── store.py
        ├── renderers/
        │   ├── __init__.py
        │   ├── protocol.py
        │   ├── connection.py
        │   ├── registry.py
        │   ├── preflight.py
        │   └── scheduler.py
        ├── delivery/
        │   ├── __init__.py
        │   ├── streaming.py
        │   ├── bundle.py
        │   └── manifest.py
        └── transport/
            ├── __init__.py
            ├── http.py
            └── websocket.py
```

Do not add alternate `services/`, `controllers/`, `utils/`, `helpers/`, `adapters/` or `legacy/` trees around this structure unless a future approved architecture explicitly changes it.

The following old API execution files/contracts must not survive as compatibility paths:

```text
dryv_api/service.py
dryv_api/stdio.py
dryv_api/subprocess_author.py
dryv_api/subprocess_render.py
AuthorSession registration
Author Backend build request fields
planningCandidates wire input
renderSessionIds wire input
previousManagedOutputs Runtime input
projectSnapshot Runtime input
```

## Runtime terminal product

Dryv Runtime has one generation terminal product: `GenerationPlan`.

Runtime must not:

- execute templates;
- own Render Client sessions;
- schedule network renderer capacity;
- own generated file bytes;
- build ZIP files;
- compare generated bytes against local files;
- write project files.

A complete `GenerationPlan` must contain enough information for `dryv-api` to execute rendering without reinterpreting pack semantics.

## API execution rule

`dryv-api` may create a Runtime/build session for a request, but it must not become a second semantic engine.

The required order is:

```text
receive and normalize build resources
    ↓
Runtime validates and produces GenerationPlan
    ↓
API reads renderer requirements from the plan
    ↓
API verifies matching Render Clients exist
    ↓
API performs template/context preflight
    ↓
API schedules render jobs with bounded concurrency
    ↓
API receives generated artifacts
    ↓
API streams artifacts or creates deterministic bundle
    ↓
Project Client applies locally
```

API must never independently parse pack rules to derive a competing plan.

## Stream safety

All renderer and client streaming must be bounded.

- No unbounded in-memory artifact queues.
- Backpressure belongs in `dryv-api`.
- Artifact streams carry stable artifact/job identity and deterministic plan order independent of completion order.
- Large artifacts may be chunked.
- Small artifacts may be sent inline when the protocol permits.
- Bundle download should use HTTP; WebSocket remains the progress/control channel.
- A client disconnect must have an explicit policy. Stateless V1 may cancel the build rather than retaining unbounded output.

## Bundle safety

Bundle creation is delivery infrastructure.

- Runtime must not import ZIP/TAR libraries for generated output delivery.
- Bundles must use normalized project-relative artifact paths.
- Bundles include `.dryv/manifest.json` with build/artifact identities, hashes and provenance.
- Bundle metadata should be normalized so deterministic output is possible.
- Project Clients independently validate bundle paths and hashes before extraction/apply.

## Stateful evolution

Initial implementation may be stateless.

Future account/project state must be content-addressed and must not alter semantics. The server may remember resources by server-verified hash and request only missing content. Every build still identifies exact config, IR, pack/template and renderer identities.

Do not implement account persistence, distributed storage or MCP during the current tasks unless the user explicitly expands scope.

## Stop conditions

Stop implementation and request architecture approval rather than improvising if:

- the required tree appears insufficient for a real responsibility;
- a new cross-package owner seems necessary;
- a public contract would move semantics from Runtime to API or Render Client;
- a production file cannot reasonably remain within the 500-line maximum;
- a compatibility layer seems necessary;
- test behavior conflicts with this approved architecture.

Architecture is changed by explicit user decision, not by implementation convenience.
