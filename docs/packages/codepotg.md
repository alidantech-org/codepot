---
title: codepotg
description: The supported Python template-pack manager and Jinja generator for OpenAPI produced by codepot-openapi or other compatible sources.
product: codepotg
order: 11
---

# `codepotg`

`codepotg` is the stable Python and Jinja generation runtime in the Codepot ecosystem.

It consumes OpenAPI 3.0 or 3.1 JSON/YAML, performs inference, builds normalized generator contexts, resolves output dependencies, and renders bundled or project-owned Jinja template packs.

The package is mature, supported, and used in real projects.

## Install

```bash
python -m pip install codepotg
```

Verify the installation:

```bash
codepotg --version
codepotg --help
python -m codepotg --version
```

## What it owns

- streamed JSON input through an indexed JSONL cache and cached YAML compatibility conversion;
- normalized generation contracts;
- inference for schemas, operations, resources, entities, access, and frontends;
- Jinja templates, partials, filters, and legacy or selection-graph path expressions;
- bundled TypeScript, Next.js, Dart, and debug template packs;
- custom project-owned packs;
- dependency and import planning;
- managed and immutable file modes;
- guarded refresh cleanup;
- dry runs, commands, diagnostics, and reports;
- bounded graph contexts, explicit dependency providers, barrels, lazy resolvers, and atomic writes;
- optional memory-stage tracing and diagnostic snapshots;
- optional Codepot `x-codegen` metadata.

## Quick start

Create a configuration:

```bash
codepotg init --yes
```

`Codepotg.yaml`:

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    output: ./generated/sdk
```

Preview:

```bash
codepotg generate sdk --dry-run --verbose
```

Generate:

```bash
codepotg generate sdk
```

Run every task:

```bash
codepotg generate --all
```

## Configuration ownership

The Python package intentionally uses `Codepotg.yaml`.

`CodepotFile.yml` and `CodepotFile.yaml` belong to the JavaScript `codepotx` workflow and are rejected by CodepotG. Keeping distinct filenames prevents a project from accidentally running a task with the wrong engine.

A task supports:

| Field | Purpose |
|---|---|
| `input` | OpenAPI JSON or YAML document |
| `language` | Bundled adapter such as `typescript`, `next`, `dart`, or `debug` |
| `output` | Generated output root |
| `templateDir` / `templates` | Optional custom Jinja pack |
| `clean` | Paths eligible for guarded refresh cleanup |
| `before` / `after` | Project-owned commands |
| `env` | Task environment values |
| `frontend` | Explicit frontend selection |
| `description` | Human-readable task description |

`allow: true` is mandatory before generation.

## Custom template packs

```yaml
allow: true

tasks:
  custom-sdk:
    input: ./openapi.json
    language: typescript
    templateDir: ./templates/typescript
    output: ./generated/sdk
```

CodepotG supports two compatible pack models:

- legacy `folders`, using the established full compatibility contract;
- named `selections`, `emissions`, and `barrels`, using bounded contexts and an explicit dependency graph.

New graph packs can declare providers, schedule barrels after their emitted members, resolve source records lazily from indexed JSONL, and keep render queues bounded. Existing folder packs remain supported during migration.

A pack uses Jinja templates and `paths.yaml` to control:

- which normalized collections are selected;
- aliases exposed to a template;
- output folders and filenames;
- raw and static files;
- imports and dependencies;
- managed, immutable, protected, and clean roots.

## Lifecycle policy

```yaml
write_policy:
  default_mode: managed
  managed_roots: [generated]
  immutable_roots: [src]
  protected_roots: [src]
  clean_roots: [generated]
```

Managed files may be refreshed only inside managed roots. Immutable files are created once and preserved. Cleanup is restricted to known generated ownership and configured safe roots.

## Performance and memory paths

JSON input is streamed into an indexed JSONL cache. YAML is parsed through a compatibility path and persisted as canonical JSON so unchanged YAML sources can reuse the conversion.

```bash
python scripts/profile_memory.py tests/fixtures/openapi.json --full --emit --json
CODEPOTG_MEMORY_TRACE=full codepotg generate sdk
```

The package can record stage snapshots for JSONL readiness, document loading, graph inference, contract creation, template planning, emission, and release.

## Input from `codepot-openapi`

The primary Codepot prototype workflow is:

```text
codepot-openapi
    ↓
OpenAPI JSON/YAML + x-codegen
    ↓
codepotg
    ↓
Jinja template pack
    ↓
generated files
```

Plain OpenAPI fields remain useful without extensions. `x-codegen` adds richer resource placement, entity roles, access, frontend definitions, hooks, and documentation metadata.

## Frontend metadata

When the document contains `x-codegen.frontends`, a task may select a frontend:

```yaml
frontend: admin
```

Use `frontend: "*"` to expose all explicitly authored frontends. CodepotG does not invent screens or components.

## Python API

```python
from pathlib import Path
from codepotg import GeneratorApp

app = GeneratorApp()
result = app.generate(
    config_path=Path("Codepotg.yaml"),
    task_name="sdk",
    dry_run=True,
    verbose=True,
)
```

## Relationship to `codepotx`

`codepotx` is the official JavaScript rewrite where validated generation behavior is stabilized behind frontend-neutral runtime operations.

CodepotG remains supported while that rewrite reaches the required maturity and compatibility. A future migration may reduce the need for the Python workflow, but that is not the current release status.

## Development and validation

```bash
cd packages/python/codepotg
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python scripts/release.py check
```

The published package requires Python 3.11 or newer. Detailed template-authoring, normalized-contract, graph-path, compatibility, lossless OpenAPI, language-adapter, and performance guides remain under `packages/python/codepotg/docs/`.
