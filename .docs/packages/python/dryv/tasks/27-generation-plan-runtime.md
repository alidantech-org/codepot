# Task 27 — Build the GenerationPlan Runtime

Status: [x]
Owner: `packages/python/dryv`
Depends on: Task 26

## Goal

Implement the final Dryv Runtime so `dryv.yaml + Canonical Dryv IR + normalized pack resources` deterministically produce one complete `GenerationPlan` and transport-neutral progress/diagnostics.

Runtime stops at the plan. It must not render templates or own generated artifact bytes.

## Required public Runtime flow

```text
RuntimeInput
    ↓
load/validate usage configuration
    ↓
load/validate/index Canonical IR
    ↓
load/validate packs
    ↓
resolve options/relationships
    ↓
evaluate template selection
    ↓
build semantic + generation dependency graph
    ↓
construct canonical contexts
    ↓
resolve planned output paths
    ↓
hash deterministic inputs
    ↓
GenerationPlan
```

## Required Runtime files

```text
dryv/runtime/
├── __init__.py
├── contracts.py
├── events.py
└── runtime.py
```

### `contracts.py`

Own only Runtime boundary data such as:

```text
RuntimeInput
RuntimeResource
RuntimePack
RuntimePackResource
RuntimeDiagnostic
RuntimeResult
```

Planning owns the `GenerationPlan`/RenderJob planning data contracts consumed through its public Feature root.

### `events.py`

Own transport-neutral Runtime events and the event sink/observer contract.

### `runtime.py`

Own the small Runtime composition root. It coordinates approved Features and returns the complete plan.

## Implemented planning completeness

Every `RenderJob` carries deterministic execution data for `dryv-api` without API-side pack reinterpretation:

- stable job identity and topological order;
- semantic subject identity/kind;
- pack/template selection reason;
- renderer capability requirement;
- template logical resource identity, path, media type and content hash;
- canonical JSON-compatible context;
- context contract/version/hash;
- planned artifact ID and normalized project-relative path;
- semantic and render-job dependencies.

Pack manifests now directly declare selections and templates. Clients no longer construct `PlanningCandidate` values.

## Context rule

Runtime owns context meaning. Render Clients receive canonical JSON-like values, never Canonical IR model objects.

Schema jobs include effective inherited Schema information. Context also contains semantic dependencies, planned artifact/dependency paths, pack options/bindings and selection facts.

## Pack rule

Only Packs/Planning interpret `dryv.pack.yaml` selection/binding/output semantics. `dryv-api` does not need to parse pack rules again.

The implemented template declaration owns:

```text
selection
file
renderer
output
dependsOn
```

## Runtime progress

Runtime accepts a pure-data event sink and emits transport-neutral stages:

```text
started
project
ir
packs
planning
complete
failed
```

## Forbidden implementation

The completed Engine does not:

- execute Jinja/Handlebars/another template engine;
- connect to Render Clients;
- inspect renderer URLs/capacity;
- build artifact byte streams;
- compare local files;
- create ZIP/TAR bundles;
- write files;
- execute shell/Git;
- preserve the removed Runtime architecture through compatibility aliases.

## Completion evidence

Completed on `develop` without test changes.

- Production root is only `features`, `ir`, `runtime`, `versions`, `__init__.py`, and `py.typed`.
- The Feature tree matches the approved file/folder architecture exactly.
- Project parsing contains no Author Backend/renderer connection configuration.
- Canonical IR JSON, YAML and JSONL decoding is owned by Serialization.
- Pack manifests own canonical selection and template declarations.
- Planning derives jobs directly from Canonical IR + packs and constructs contexts, context contracts, dependencies, planned artifact paths, renderer requirements and plan hashes.
- `DryvRuntime.plan()` registers explicit resources, validates `dryv.yaml`, decodes/validates/indexes Canonical IR, validates resolved pack bundles and returns `GenerationPlan`.
- The old `Group.workflows` migration path and explicit legacy `OperationFailure` value were removed rather than shimmed.
- Runtime progress remains transport-neutral.
- Current production source files are below the 500-line ceiling by inspection.
- No tests were added, modified, deleted, or used to restore removed architecture.

Executable test certification remains intentionally deferred until the user approves the final production architecture/code. The next work is `dryv-api` Task 00.
