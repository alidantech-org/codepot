# Dryv runtime orchestration

## Purpose

The runtime composes canonical contracts, project and pack configuration, fixed selectors, plugins, artifact planning, rendering, and writers into deterministic generation operations.

It does not introduce another semantic model or allow providers, plugins, packs, or interfaces to bypass planning.

```text
dryv.yaml or host request
        ↓ strict configuration
contract provider
        ↓ immutable Contract
core validation
        ↓
pack resolution + DryvPack.yaml
        ↓
fixed selector invocations
        ↓
complete artifact/dependency/path plan
        ↓ only when ready
bounded immutable contexts
        ↓
template engine + target validation
        ↓
MemoryOutput
        ├── deterministic archive
        └── managed transactional filesystem
```

## Current public operations

```python
from dryv import generate, generate_to_files

plan_result = generate("dryv.yaml", dry_run=True)
memory_result = generate("dryv.yaml")
file_result, write_report = generate_to_files("dryv.yaml")
```

These functions remain compatibility-level public operations while the `DryvRuntime` facade is introduced.

Planned facade:

```python
from dryv import DryvRuntime

runtime = DryvRuntime.discover()
project = runtime.load_project("dryv.yaml")
plan = runtime.plan(project)
report = runtime.generate_to_files(project)
```

Command parsing and terminal output move to the standalone `dryv-cli` package.

## Supported first production scope

- strict YAML/JSON `dryv.yaml` decoding;
- strict `DryvPack.yaml` decoding;
- built-in canonical IR JSON/YAML loading;
- project-contained local packs;
- pack compatibility requirements;
- ignore rules and symlink containment;
- template, partial, static, and binary discovery;
- longest engine and target suffix inference;
- fixed selector registry and selection-folder fan-out;
- safe path expressions;
- output collision and target-path validation;
- symbols, imports, exports, and generated provider matching;
- bounded relationship-aware contexts;
- cancellation and structured diagnostics;
- deterministic memory and archive output;
- managed transactional filesystem output;
- ownership state, manual-edit protection, and safe stale deletion;
- dry-run plans and artifact explanation.

## Separate capability lanes

### Python contract provider

A configured module/callable provider is planned so `dryv-author` can return an in-memory `Contract` without an intermediate file.

### Git pack provider

Remote packs remain a dedicated trust/lock lane. The local runtime fails safely instead of downloading executable content without immutable identity and credential controls.

### Commands

Project and pack commands remain fail-closed until exact planning, provenance, approvals, host policy, timeout, cleanup, cancellation, and phase reporting are implemented.

### Incremental generation

The runtime currently creates a complete deterministic plan and output. Incremental generation begins only after impact analysis and byte-for-byte equivalence with full generation are proven.

### Cross-operation cache

Template engines may own bounded instance caches. A runtime content cache remains a separate public port and behavior-key design task.

## Phase 1 — Configuration

Unknown fields, duplicate keys, recursive values, unsafe paths, non-finite numbers, excessive depth, and oversized configuration trees fail before plugin or pack work.

Values are frozen into immutable sorted structures before crossing subsystem boundaries.

## Phase 2 — Plugin composition

Current entry-point groups:

```text
dryv.source_adapters
dryv.language_adapters
dryv.template_engines
```

Each entry point loads a zero-argument factory returning the published protocol. The runtime rejects duplicate IDs/aliases, failed factories, protocol mismatches, ambiguous suffixes, and missing requested capabilities.

Plugin instances are session-owned. Importing a package does not mutate a global registry.

## Phase 3 — Contract loading

The current file route passes an authorized location and immutable options to the built-in canonical IR loader. It returns a `Contract`, optional digest, and diagnostics.

Future contract providers may return the same public `Contract` directly. No planning occurs when provider or semantic validation reports errors.

## Phase 4 — Pack discovery

A local pack remains contained beneath the project root and contains:

```text
DryvPack.yaml
templates/
```

Discovery validates compatibility, selections, dependency cycles, ignore rules, containment, file classifications, partials, engines, and targets. Files without an engine suffix are copied exactly as static or binary artifacts.

## Phase 5 — Semantic selection

Selectors are fixed, versioned, and introspectable. Packs select only registered roots. A selector producing no contexts emits no artifacts. Literal files outside a semantic selection emit once.

## Phase 6 — Artifact planning

Every artifact receives a stable identity separate from destination. Planning fixes the pack, selection, semantic cause, template/static identity, engine, target, path, scope, symbols, options, bindings, and generated dependencies.

The plan rejects unsafe destinations, collisions, duplicate identities, invalid paths/expressions, unknown selections, missing inputs, and ambiguous providers before rendering.

## Phase 7 — Generated dependencies

After all provider artifacts exist, the runtime resolves declared imports and exports. Target plugins receive planned paths and return module/path facts only. Templates author all import/export syntax.

## Phase 8 — Prepared context

One bounded immutable context is prepared per artifact. It contains documented semantic and planning facts only. Filesystem handles, providers, writers, executors, caches, environments, secrets, authoring builders, and runtime singletons never enter templates.

## Phase 9 — Rendering

The engine receives a template ID, UTF-8 source, immutable context, declared partials, and cancellation. Static/binary files bypass rendering. Any error stops before filesystem commit.

## Phase 10 — Memory output

Successful generation first creates sorted deterministic `MemoryOutput`. This is the common source for tests, target compiler checks, archives, filesystem output, IDE previews, and structured service adapters.

## Phase 11 — Writers

Archive output uses sorted paths and fixed metadata so equal input produces equal bytes.

Managed filesystem state lives at:

```text
.dryv/generation-state.json
```

Rules:

- unmanaged conflicts are never overwritten;
- unchanged managed files may be updated;
- manually edited managed files are protected;
- unchanged stale managed files may be removed;
- changed stale files are protected and released;
- output and state commit transactionally;
- failures roll changes back.

Generated output hashes remain in ownership state, not `dryv.lock.yaml`.

## Error guarantee

- invalid configuration stops before plugin composition;
- invalid provider results stop before packs;
- invalid IR stops before selection;
- invalid packs stop before planning;
- invalid plans stop before rendering;
- render failures stop before writing;
- writer failures preserve or restore the destination and state.

No partially valid plan is rendered.

## Verification gate

```bash
cd packages/python/dryv
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```

Then install the runtime, authoring, Jinja, TypeScript, and Dart wheels in a fresh environment and repeat plugin discovery plus the direct IR and Python authoring manual routes.
