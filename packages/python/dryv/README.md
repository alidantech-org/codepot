# dryv

`dryv` is the transport-neutral semantic Runtime for Dryv.

It owns Canonical Dryv Runtime IR meaning and deterministically turns validated Usage configuration, Canonical IR, and already-resolved Template Pack bundles into an inspectable `GenerationPlan`.

```text
dryv.yaml
+ Canonical Dryv Runtime IR
+ resolved pack manifests/resources
        ↓
    Dryv Runtime
        ↓
 validation / IR indexing
 pack validation / selection
 canonical contexts
 dependency graph
 planned output paths
 provenance / trace
        ↓
   GenerationPlan
```

## Ownership boundary

`dryv` owns:

- Canonical Runtime IR models and validation;
- Runtime IR decoding/encoding and inspection support;
- `dryv.yaml` semantic validation;
- Template Pack manifest meaning;
- deterministic pack selection over canonical IR;
- context and context-contract construction;
- semantic/render dependency planning;
- planned artifact identities and project-relative output paths;
- deterministic hashes, diagnostics and traceability;
- the `GenerationPlan` returned to the outer host.

`dryv` does **not**:

- execute Author implementations;
- discover local files or clone Git repositories;
- host HTTP or WebSockets;
- select renderer endpoints or machines;
- execute Jinja, Handlebars or any other template engine;
- own renderer capacity or network scheduling;
- contain generated artifact bytes;
- create ZIP bundles;
- read or mutate the user's project filesystem;
- execute project shell commands.

Those responsibilities belong to Author Backends, `dryv-api`, Render Clients and Project Clients respectively.

## Canonical architecture

```text
Authoring source
      ↓
Author Backend
      ↓
Canonical Dryv Runtime IR
      │
      ├──────── dryv.yaml
      └──────── resolved Template Pack bundles
                    ↓
                DryvRuntime
                    ↓
              GenerationPlan
                    ↓
                 dryv-api
                    ↓
              Render Client(s)
                    ↓
                 artifacts
                    ↓
              Project Client
                    ↓
                 filesystem
```

Canonical Runtime IR is the only semantic authority. Authoring implementations may be written in Python, TypeScript, Rust, Codepot language, or another language as long as they compile to the same versioned IR contract.

## Packs and planning

A Template Pack declares generation behavior using the same Dryv vocabulary as Canonical IR. A pack identifies:

- the canonical kinds/selections it reacts to;
- template resources;
- logical renderer capability requirements such as `jinja`;
- output path patterns;
- template dependencies;
- options and project bindings.

Packs never contain renderer URLs or redefine software meaning.

Planning produces `GenerationPlan` jobs containing exact template identities/hashes, canonical context, context contracts, renderer capability requirements, dependencies, planned artifacts and provenance. Runtime stops there.

## Determinism

Semantic plan identity depends on canonical input/configuration/resource identities, not an ephemeral build ID or network connection identity. The same semantic inputs can therefore produce the same `planHash` even when individual build executions use different request IDs.

## Project ownership

Only a Project Client knows the user's actual filesystem. The reference `dryv-cli` Project Client receives generated artifacts from `dryv-api`, verifies their identities and hashes, computes local conflicts/diffs and applies approved changes atomically. Runtime never writes user files.

## Current companion packages

Reference implementations live beside `dryv-api`:

```text
packages/python/dryv-api/.helpers/
├── dryv-author
├── dryv-template-jinja
└── dryv-cli
```

They preserve the same architectural boundaries rather than becoming Runtime plugins.
