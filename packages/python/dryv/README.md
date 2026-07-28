# Dryv

Dryv is the clean-room rewrite of the Python generation runtime. This directory contains the approved closed semantic kernel, project/pack contracts, adapter boundaries, implementation stages, package task tracking, and the first public implementation foundation.

The existing `packages/python/dryv` package remains untouched and serves only as a source of real requirements and representative outputs. New implementation must not import its internals or reproduce its global registries, raw YAML processing, CLI-centered logic, OpenAPI leakage, overlapping emission paths, or old configuration runtime.

## Implemented source structure

The implementation follows the approved package architecture instead of placing unrelated contracts in flat modules:

```text
src/dryv/
├── __init__.py
├── api/
│   ├── cancellation.py
│   └── results.py
├── application/
├── config/
├── diagnostics/
│   ├── model.py
│   └── source.py
├── domain/
│   ├── ir/
│   │   ├── base.py
│   │   ├── events.py
│   │   ├── facets.py
│   │   ├── groups.py
│   │   ├── naming.py
│   │   ├── operations.py
│   │   ├── policies.py
│   │   ├── schemas.py
│   │   ├── storage.py
│   │   ├── types.py
│   │   ├── validation/
│   │   │   ├── index.py
│   │   │   └── validator.py
│   │   ├── views.py
│   │   └── workflows.py
│   └── generation/
│       └── selectors.py
├── generation/
├── infrastructure/
├── ir/
├── plugins/
│   ├── descriptors.py
│   └── registry.py
├── ports/
│   ├── source.py
│   ├── target.py
│   └── templates.py
├── runtime/
├── testing/
│   └── conformance.py
├── versions/
│   └── model.py
├── cli/
└── py.typed
```

The public `dryv.ir` and `dryv.generation` packages are explicit facades over the internal domain packages. There are no same-name flat modules such as `ir.py`, `plugins.py`, or `ports.py` beside package directories.

## Implemented test structure

Tests mirror the production boundaries:

```text
tests/
├── architecture/
├── contracts/
│   └── ports/
├── distribution/
├── fixtures/
└── unit/
    ├── api/
    ├── diagnostics/
    ├── domain/
    │   ├── generation/
    │   └── ir/
    ├── plugins/
    └── versions/
```

The architecture suite rejects flat source dumps, root-level `test_*.py` files, same-name module/package collisions, old-runtime imports, and invalid dependency direction.

## Implemented foundation

The initial `dryv` package now provides:

- dependency-free Python 3.11+ packaging under the future `dryv` namespace;
- semantic/API/behavior version values;
- source identities, spans, immutable diagnostics, cancellation, statuses, and operation results;
- the exact `name.<case>.<number>` projection contract;
- a closed typed IR for groups, structural schemas, operations, known facets, views, storage mappings, policies, events, listeners, execution hooks, workflows, and compensation;
- cross-reference validation before generation;
- fixed root-first selectors such as `groups.operations.each` and `groups.storage.mappings.each`;
- immutable plugin descriptors and registry conflict diagnostics;
- public source-adapter, target-adapter, and template-engine protocols;
- reusable conformance helpers for independently developed adapter packages;
- unit, connected-contract, conformance, import-smoke, architecture-boundary, and isolated-wheel tests.

This foundation is intentionally not a generator yet. It is the public contract that allows `dryv-openapi`, TypeScript/Dart target adapters, and the Jinja engine to be implemented in parallel without importing private core code.

## Parallel package imports

OpenAPI/source adapters use:

```python
from dryv.diagnostics import Diagnostic, Diagnostics
from dryv.ir import Contract, Group, Operation, Schema
from dryv.ports import SourceAdapter, SourceAdapterRequest, SourceAdapterResult
```

Target adapters use:

```python
from dryv.ports import (
    IdentifierValidationRequest,
    ModulePathFacts,
    ModulePathRequest,
    OutputPathValidationRequest,
    TargetAdapter,
    TargetDescriptor,
)
```

Template engines use:

```python
from dryv.ports import RenderRequest, RenderResult, TemplateEngine
```

All adapter packages can run the same public conformance helpers from `dryv.testing`.

## Local verification

From this package directory:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests
python -m build
```

The first user-run verification found a setuptools license-classifier conflict, one wheel-build test failure caused by that conflict, and Ruff findings in the initial flat implementation. The classifier and reported Ruff categories have been corrected while reorganizing the source and tests. The reorganized tree remains under verification until the complete command sequence passes again.

No GitHub workflow is required or added.

## Primary goals

- Make the importable Python application API the primary interface.
- Keep CLI, servers, playgrounds, notebooks, IDE, and MCP tools as thin adapters.
- Replace raw configuration dictionaries with immutable typed contracts.
- Maintain a closed, typed, versioned semantic kernel owned only by core.
- Model groups, structural schemas, operations, views, storage mappings, policies, events, workflows, and known facets through clear typed relationships.
- Use fixed root-first selectors and outer-to-inner template contexts.
- Treat `dryv.yaml` as project orchestration and `DryvPack.yaml` as the pack contract.
- Let templates, macros, partials, and static files own every emitted character.
- Use target adapters only for suffix detection, target validation, and module/path facts.
- Support heterogeneous packs containing code, configuration, documentation, static files, and binary assets.
- Discover source, target, template-engine, ecosystem, pack-provider, writer, cache, and command adapters through normal Python packages and entry points without allowing semantic extension.
- Plan every semantic reference, artifact identity, output, symbol, dependency, binding, command, approval, and impact relationship before rendering.
- Explain artifacts and provide deterministic dry-run/blast-radius information.
- Commit filesystem output transactionally and support memory/archive writers.
- Prove deterministic full generation before conservative incremental generation.
- Re-author projects and packs into v2 without embedding old decoders or execution paths.

## Non-goals

- arbitrary third-party semantic objects, facets, selectors, or graph-query DSLs;
- neutral `resource`, `model`, `entity`, `frontend`, or `ui` roots;
- language adapters that render types, literals, imports, exports, comments, validators, decorators, or framework syntax;
- hidden pack profiles, `filePatterns`, or explicit ordinary-file registries;
- generated output hashes in the dependency lock.

## Documentation

Start with [`docs/README.md`](docs/README.md), [`docs/00-governance/00-approved-architecture.md`](docs/00-governance/00-approved-architecture.md), and [`docs/00-governance/04-closed-semantic-kernel.md`](docs/00-governance/04-closed-semantic-kernel.md).

The implementation backlog is in [`docs/tasks/00-master-plan.md`](docs/tasks/00-master-plan.md), parallel ownership is in [`docs/tasks/PARALLEL_WORK.md`](docs/tasks/PARALLEL_WORK.md), and evidence is recorded in [`docs/tasks/PROGRESS.md`](docs/tasks/PROGRESS.md).

## Status

Foundation implementation and corrective verification are in progress on `chatgpt/codepotx-restart`. Configuration decoding, pack discovery, artifact planning, rendering, writing, and CLI work remain future task lanes.
