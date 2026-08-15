# dryv

Code: `packages/python/dryv`

Status: active architecture refactor. The implementation sequence is enforced through [`tasks/`](tasks/), with `.docs/TODO.md` pointing to the single active task.

## Approved architecture direction

Dryv Engine is the deterministic semantic/planning runtime. It does not own frontend UI, project filesystem mutation, author implementation languages, template execution processes, or HTTP/WebSocket hosting.

```text
Author Backend
    ↓ Canonical Dryv IR

Project Client
    ↓ dryv.yaml + logical resources + previous managed outputs

Network host when used
    ↓
Dryv Runtime
    ↓ coordinates independent Features
    ↓
AuthorSession / RenderSession when required
    ↓
Artifact + WriteInstruction stream
    ↓
Project Client
    ↓
user filesystem apply
```

## Runtime and Feature boundaries

Runtime is the composition root. Independent capabilities live under `dryv.features.*` and are consumed through each Feature package root.

The approved Feature catalog is:

```text
dryv.features.serialization
dryv.features.project
dryv.features.resources
dryv.features.hashing
dryv.features.ir
dryv.features.packs
dryv.features.planning
dryv.features.cache
dryv.features.authoring
dryv.features.templating
dryv.features.scheduling
dryv.features.artifacts
dryv.features.diagnostics
```

Boundary rules are executable policy under `packages/python/dryv/tests/architecture/`:

- `dryv.ir` does not import Runtime or Features.
- Features do not import Runtime.
- Features do not import sibling Features.
- production consumers import a Feature through its public package root, not a private path;
- Runtime is the only owner allowed to coordinate multiple Features;
- vague Feature buckets such as `common`, `utils`, `helpers`, `misc`, and `shared` are rejected;
- server-hosting dependencies and server-framework imports are rejected from `dryv`.

The pre-Feature `api`, `application`, `config`, `diagnostics`, `domain`, `generation`, `infrastructure`, `plugins`, `ports`, `testing`, and `versions` packages are temporary migration surfaces, not alternate architectural owners. Their exception is explicit in the architecture tests and is bounded by Task 21. Engine-side project writers remain temporary Task 21 exceptions as well.

## Canonical meaning

Canonical Dryv IR remains the only semantic authority. The working concept family includes:

```text
Contract
├── Groups
│   ├── Properties
│   ├── Schemas
│   ├── Policies
│   ├── Failures
│   ├── Events
│   ├── Operations
│   ├── StorageMappings
│   ├── ValueSources
│   └── Views
├── Workflows
└── Presentations
```

Cross-cutting information includes tags, guidance, documentation, provenance, and typed references.

Schema supports the approved zero-or-one direct base Schema extension model with transitive chains and explicit overrides. Relationship owners author forward relationships; Runtime may derive reverse indexes for inspection and template context.

`dryv.yaml` is usage configuration. `dryv.pack.yaml` defines pack/generation behavior. Canonical IR may be represented as JSON, YAML, or JSONL; these are representations of the same semantic contract.

## External boundaries

- Author Backends compile authored source to Canonical Dryv IR and may run independently.
- Render Clients receive template content plus canonical JSON context and return generated logical output bytes.
- Project Clients collect local/private resources and safely apply Artifact/WriteInstruction streams.
- A separate API/network package may host Dryv Runtime over HTTP/WebSocket for local or remote frontends.

Dryv generation must remain deterministic, explainable, portable, bounded, cache-safe, and fully traceable from semantic input through planned artifacts.

## Tasks

Implementation tasks live under [`tasks/`](tasks/) and must be executed in dependency order. `.docs/TODO.md` points to the currently active task only.
