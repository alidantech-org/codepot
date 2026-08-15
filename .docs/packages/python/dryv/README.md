# dryv

Code: `packages/python/dryv`

Status: active architecture refactor planning. The approved implementation sequence starts at [`tasks/00-runtime-feature-boundaries.md`](tasks/00-runtime-feature-boundaries.md).

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

## Engine structure

The refactor organizes independent capabilities under `dryv.features.*`, with Runtime as the only composition root. Planned Features include serialization, project configuration, resources, hashing, IR validation/indexing, packs, planning, cache, authoring sessions, templating sessions, scheduling, artifacts, and diagnostics.

`dryv.yaml` is usage configuration. `dryv.pack.yaml` defines pack/generation behavior. Canonical IR may be represented as JSON, YAML, or JSONL; these are representations of the same semantic contract.

## External boundaries

- Author Backends compile authored source to Canonical Dryv IR and may run independently.
- Render Clients receive template content plus canonical JSON context and return generated logical output bytes.
- Project Clients collect local/private resources and safely apply Artifact/WriteInstruction streams.
- A separate API/network package may host Dryv Runtime over HTTP/WebSocket for local or remote frontends.

Dryv generation must remain deterministic, explainable, portable, bounded, cache-safe, and fully traceable from semantic input through planned artifacts.

## Tasks

Implementation tasks live under [`tasks/`](tasks/) and must be executed in dependency order. `.docs/TODO.md` points to the currently active task only.
