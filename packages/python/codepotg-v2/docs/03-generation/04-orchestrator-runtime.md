# CodepotG v2 orchestrator runtime

## Purpose

The orchestrator composes the closed IR, project and pack contracts, fixed selectors, source adapters, template engines, target adapters, artifact planning, rendering, and writers into one deterministic generation operation.

It does not introduce another semantic model or allow adapters to bypass planning.

```text
codepotg.yaml
    ↓ strict decode
source adapters
    ↓ immutable Contract
core validation
    ↓
local pack discovery + CodepotgPack.yaml
    ↓
fixed selector invocations
    ↓
complete artifact/dependency/path plan
    ↓ only when ready
bounded render contexts
    ↓
template engine + target validation
    ↓
MemoryOutput
    ├── deterministic ZIP
    └── managed transactional filesystem
```

## Implemented public operations

Python:

```python
from codepotg import generate, generate_to_files

plan_result = generate("codepotg.yaml", dry_run=True)
memory_result = generate("codepotg.yaml")
file_result, write_report = generate_to_files("codepotg.yaml")
```

CLI:

```bash
codepotg plan codepotg.yaml
codepotg generate codepotg.yaml --memory
codepotg generate codepotg.yaml
codepotg generate codepotg.yaml --destination ./generated-review
```

The CLI calls the same application services. It has no alternate planner or writer logic.

## Supported first production scope

The implemented orchestrator supports:

- strict YAML/JSON `codepotg.yaml` decoding;
- strict `CodepotgPack.yaml` decoding;
- local semantic source files;
- source adapters discovered through Python entry points;
- the built-in canonical IR JSON/YAML source adapter;
- project-contained local pack sources;
- pack compatibility requirements for CodepotG and IR versions;
- Gitignore-compatible include/exclude rules;
- pack-root `.gitignore` filtering;
- symlink containment;
- template, partial, static, and binary discovery;
- longest template-engine suffix inference;
- longest target suffix inference;
- the published fixed selector registry;
- selection-folder fan-out;
- `(expression)` and `((literal))` path evaluation;
- output collision and path validation;
- explicit symbols, imports, and exports;
- generated provider matching by semantic identity and group scope;
- target-adapter module/path facts;
- static selection-cycle detection;
- bounded relationship-aware render contexts;
- cancellation;
- memory output;
- deterministic ZIP output;
- managed transactional filesystem output;
- ownership state and safe stale deletion;
- dry-run plan documents and artifact explanation.

## Deliberately separate capability lanes

The runtime fails rather than silently ignoring declarations that require another trust subsystem.

### Git pack provider

`source.git` remains a dedicated Git/lock lane. The current local-pack orchestrator reports `PACK_PROVIDER_UNSUPPORTED` for Git pack instances. It does not treat a Git URL as a local path or download code without lock and trust controls.

### Commands

Project, pack-instance, or pack-owned commands report `CMD_APPROVAL_REQUIRED` until the command planning, digest, host-policy, approval, timeout, cleanup, and phase-reporting subsystem is installed.

Commands are never executed through a shell by the current orchestrator.

### Incremental generation

The current orchestrator always creates a complete deterministic plan and complete rendered output. Conservative incremental generation starts only after full-generation equivalence and impact analysis are proven.

### Cache

Template engines may own bounded instance caches. A cross-operation content cache remains a separate cache-port lane.

These are not silent TODO paths. Their declarations fail readiness with stable diagnostics.

## Phase 1 — Configuration

The loader accepts only the approved project and pack fields.

Unknown fields, duplicate YAML/JSON keys, recursive values, unsafe paths, non-finite numbers, excessive depth, and oversized option trees fail before plugin discovery.

Configuration values are frozen into immutable sorted tuple structures before crossing subsystem boundaries.

## Phase 2 — Plugin composition

Runtime plugins are discovered from:

```text
codepotg.source_adapters
codepotg.language_adapters
codepotg.template_engines
```

Each entry point must load a zero-argument factory returning the published protocol.

The runtime rejects:

- duplicate plugin IDs or aliases;
- failed factories;
- objects that do not implement the public protocol;
- ambiguous target suffixes;
- ambiguous engine suffixes;
- missing requested adapters.

Plugin instances are session-owned. No process-global instance registry is used.

## Phase 3 — Source normalization

Every project source is contained beneath the project root, including after symlink resolution.

The selected source adapter receives:

```text
source_id
absolute authorized location
immutable adapter options
cancellation token
```

A source result contributes:

```text
Contract | None
digest | None
Diagnostics
```

No planning occurs when source diagnostics contain errors.

## Phase 4 — Pack discovery

A local pack must remain inside the project root and contain:

```text
CodepotgPack.yaml
templates/
```

Discovery:

1. validates manifest compatibility;
2. validates selection references and dependency cycles;
3. applies manifest include patterns;
4. applies manifest exclude patterns;
5. applies pack-root `.gitignore`;
6. rejects symlink escape;
7. classifies every included file;
8. registers partials without emitting them;
9. infers engines and targets by longest suffix.

A file with no recognized engine suffix is static/binary and is copied exactly.

## Phase 5 — Semantic selection

Selectors are fixed and introspectable. Packs select only registered roots.

The current registry is listed in [`../01-foundation/05-authoring-aligned-ir.md`](../01-foundation/05-authoring-aligned-ir.md).

A selector returning zero contexts emits zero artifacts. It does not run once with an empty context.

A literal file outside a semantic selection emits once.

## Phase 6 — Artifact planning

Every artifact receives a stable identity separate from its destination:

```text
pack instance
selection key or literal
selected semantic ID or once
pack template path
```

The first pass plans:

- invocation;
- output path;
- template/static identity;
- engine;
- target;
- selected semantic identity;
- group scope;
- declared symbols.

No renderer or writer runs during this pass.

The plan rejects:

- unsafe destinations;
- output collisions;
- duplicate artifact identities;
- target-invalid paths;
- invalid expressions;
- unknown selection folders;
- missing semantic inputs;
- zero or conflicting providers.

## Phase 7 — Generated dependencies

After every artifact exists, the second pass resolves `imports` and `exports`.

Provider priority:

1. same semantic identity;
2. same group scope;
3. declared selection candidates.

The target adapter receives already planned consumer/provider paths and returns module facts. It never renders an import or export statement.

Templates receive descriptors:

```text
imports.<localName>.modules
exports.<selectionKey>.modules
module.specifier
module.artifact_path
module.semantic_id
module.symbols
```

## Phase 8 — Render context

The orchestrator prepares one bounded immutable context per artifact. See [`05-template-context-contract.md`](05-template-context-contract.md).

References needed by ordinary templates are resolved before rendering:

- operation inputs/outputs/failures to schemas;
- storage fields to schema fields;
- view triggers to operations and payload schemas;
- event schema references;
- value-source operation and fields;
- presentation entries to views;
- generated module descriptors.

Runtime, filesystem, source loader, pack provider, writer, command executor, cache store, environment, and secret objects never enter the context.

## Phase 9 — Rendering

The selected engine receives:

```text
template ID
UTF-8 source
immutable prepared context
declared partial registry
cancellation token
```

Static and binary files bypass rendering and preserve exact bytes.

Rendering failures produce diagnostics and no file commit occurs.

## Phase 10 — Memory output

Successful generation first produces a deterministic sorted `MemoryOutput`.

This is the common source for:

- tests and golden fixtures;
- generated-project compiler checks;
- ZIP output;
- filesystem output;
- IDE previews;
- HTTP/MCP adapters.

## Phase 11 — Writers

### Deterministic ZIP

`ZipArchiveWriter` uses sorted paths, fixed timestamps, fixed permissions, and exact bytes. Equal `MemoryOutput` produces equal archive bytes.

### Managed filesystem

The default file API uses `ManagedFilesystemWriter`.

State:

```text
.codepotg/generation-state.json
```

Rules:

- an unmanaged conflicting file is never overwritten;
- an unchanged managed file may change;
- a manually edited managed file is protected;
- an unchanged stale managed file may be deleted;
- a changed stale file is protected and released from management;
- output and state changes commit transactionally;
- a failure rolls replacements/deletions back.

Generated output digests remain in generation state, not `codepotg.lock.yaml`.

## Plan inspection

```python
from codepotg.generation import (
    explain_artifact,
    plan_to_document,
    plan_to_json,
)
```

The plan document contains artifact IDs, paths, templates, targets, selections, semantic causes, declared symbols, and resolved dependencies.

`explain_artifact(plan, id_or_path)` returns the exact cause chain for one artifact.

## Error guarantee

Every major phase is fail-closed:

- invalid configuration stops before plugins;
- invalid sources stop before packs;
- invalid IR stops before selection;
- invalid packs stop before planning;
- invalid plans stop before rendering;
- render failures stop before writing;
- writer failures roll back committed changes.

No partially valid plan is rendered.

## Verification gate

The orchestrator may move to complete only when all of the following run against a clean synchronized checkout:

```bash
cd packages/python/codepotg-v2
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -vv
python -m build
```

Then install the real core, OpenAPI/IR source, Jinja, TypeScript, and Dart wheels together and generate inspectable TypeScript and Dart fixture projects through entry-point discovery.

A merged implementation without this evidence remains `review`, not `complete`.
